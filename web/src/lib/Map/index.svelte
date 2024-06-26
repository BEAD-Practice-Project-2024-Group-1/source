<script lang="ts" context="module">
	import type { LngLatLike, LngLatBoundsLike, IControl } from 'maplibre-gl';
	import { MapboxOverlay as DeckOverlay } from '@deck.gl/mapbox';
	import { ScatterplotLayer, GeoJsonLayer } from '@deck.gl/layers';
	import { HeatmapLayer } from '@deck.gl/aggregation-layers';
	import 'maplibre-gl/dist/maplibre-gl.css';
	import { onDestroy, onMount } from 'svelte';
	import { pipe, debounce, makeSubject, subscribe } from 'wonka';
	import type { Feature, FeatureCollection, Point } from 'geojson';
	import * as turf from '@turf/turf';
	import dayjs from 'dayjs';
	import timezone from 'dayjs/plugin/timezone';
	import duration from 'dayjs/plugin/duration';
	import utc from 'dayjs/plugin/utc';

	dayjs.extend(utc);
	dayjs.extend(timezone);
	dayjs.extend(duration);

	const SINGAPORE_SOUTHWEST_LNLGAT: LngLatLike = [103.51461, 1.099306];
	const SINGAPORE_NORTHEAST_LNLGAT: LngLatLike = [104.162353, 1.587878];
	const MAX_BOUNDS: LngLatBoundsLike = [SINGAPORE_SOUTHWEST_LNLGAT, SINGAPORE_NORTHEAST_LNLGAT];

	export type TaxiAvailability = {
		b_id: string;
		lon: number;
		lat: number;
		created_at: string; // iso8601
	};

	enum ViewMode {
		'Streaming',
		'Timeline'
	}
</script>

<script lang="ts">
	export let planning_areas: Array<Feature> = [];

	let cache_availability_stream: Array<TaxiAvailability> = [];
	let clustered: Array<Feature> = [];

	const districts = planning_areas.map((pa) => {
		let geometries = [];
		geometries.push(turf.center(pa).geometry);
		geometries.push(pa.geometry);
		const feature: Feature = {
			id: pa.id,
			type: 'Feature',
			geometry: {
				type: 'GeometryCollection',
				geometries
			},
			properties: {}
		};

		return feature;
	});

	const taxi_availability_map = new Map<string, Array<TaxiAvailability>>();
	// full_day_taxi_availability.forEach((t) => {
	// 	const key = dayjs.utc(t.created_at).tz('Singapore').format('HHmm');
	// 	if (taxi_availability_map.has(key)) {
	// 		taxi_availability_map.get(key)?.push(t);
	// 	} else {
	// 		taxi_availability_map.set(key, [t]);
	// 	}
	// });

	let webSocketEstablished = false;
	let ws: WebSocket | null = null;

	let taxiAvailability: Array<TaxiAvailability> = [];
	let selectedTaxi: TaxiAvailability;
	let layerVisibility: Record<string, boolean> = {
		scatter: true,
		heatmap: false,
		cluster: false
	};

	let viewMode: ViewMode = ViewMode.Streaming;
	let useTimeline = false;
	let isPlaying = false;

	let time = 0;
	let noOfClusters = 2;
	let deck: DeckOverlay;

	let subject = makeSubject();
	let { source, next, complete } = subject;

	const updateDeck = (deck: DeckOverlay) => {
		deck.setProps({
			layers: [
				new GeoJsonLayer({
					id: 'planning-area-geojson',
					visible: true,
					data: districts,
					getFillColor: [0, 100, 100, 100],
					pointType: 'text',
					getText: (d: Feature) => d.id,
					getTextSize: 10,
					getLineWidth: 20,
					stroked: true,
					pickable: true
				}),
				new ScatterplotLayer<TaxiAvailability>({
					id: 'taxi-scatterplot',
					data: taxiAvailability,
					visible: layerVisibility.scatter,
					filled: true,
					radiusMinPixels: 2,
					radiusMaxPixels: 24,
					radiusUnits: 'meters',
					getFillColor: [200, 0, 80, 180],
					getPosition: (d: TaxiAvailability) => [d.lon, d.lat],
					pickable: true,
					autoHighlight: true,
					radiusScale: 1,
					onClick: (info) => {
						selectedTaxi = info?.object;
					}
				}),
				new ScatterplotLayer<Feature<Point>>({
					id: 'taxi-k-means-cluster',
					data: clustered,
					visible: layerVisibility.cluster,
					filled: true,
					radiusUnits: 'pixels',
					getFillColor: [150, 0, 150, 200],
					getPosition: (f: Feature<Point>) => f.geometry.coordinates,
					getRadius: (f: Feature<Point>) => f.properties.count,
					pickable: false,
					autoHighlight: true,
					radiusScale: 0.3,
					opacity: 1,
					parameters: {
						blend: true
					}
				}),
				new HeatmapLayer<TaxiAvailability>({
					id: 'taxi-heatmap',
					visible: layerVisibility.heatmap,
					data: taxiAvailability,
					aggregation: 'SUM',
					getPosition: (d: TaxiAvailability) => [d.lon, d.lat],
					getWeight: (d) => 1,
					radiusPixels: 50
				})
			]
		});
	};

	onMount(async () => {
		const maplibregl = await import('maplibre-gl');

		const map = new maplibregl.Map({
			container: 'map',
			style: 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json',
			center: [103.81461, 1.3521],
			zoom: 4,
			bearing: 0,
			pitch: 30,
			maxBounds: MAX_BOUNDS
		});

		map.once('load', () => {
			deck = new DeckOverlay({
				interleaved: false
			});

			map.addControl(deck as IControl);
			map.addControl(new maplibregl.NavigationControl());

			pipe(
				source,
				debounce(() => 200),
				subscribe(async () => {
					if (useTimeline) {
						const response = await fetch(`/taxi_by_time?time=${time}`);

						taxiAvailability = (await response.json()).data;
					} else {
						taxiAvailability = cache_availability_stream;
					}

					if (layerVisibility.cluster) {
						taxiAvailability;
						const fc: FeatureCollection<Point> = {
							type: 'FeatureCollection',
							features: taxiAvailability.map((ta) => {
								return {
									type: 'Feature',
									geometry: {
										type: 'Point',
										coordinates: [ta.lon, ta.lat]
									},
									properties: {}
								};
							})
						};

						const clusterAugmented = turf.clustersKmeans(fc, { numberOfClusters: noOfClusters });

						const cMap = new Map<string, Feature>();

						console.log(clusterAugmented);
						clusterAugmented.features.forEach((ca) => {
							cMap.set(ca.properties.cluster, {
								type: 'Feature',
								geometry: {
									type: 'Point',
									coordinates: ca.properties.centroid
								},
								properties: {
									cluster: ca.properties.cluster,
									count: cMap.get(ca.properties.cluster)?.properties.count + 1 || 1
								}
							});
						});

						clustered = Array.from(cMap.values());
						console.log(clustered);
					}

					updateDeck(deck);
				})
			);

			next(null); // trigger once when initialized
		});

		if (!webSocketEstablished) {
			const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';

			ws = new WebSocket(`${protocol}//${window.location.host}/websocket`);
			ws.addEventListener('open', (event) => {
				webSocketEstablished = true;
				console.debug('[websocket] connection open', event);
			});

			ws.addEventListener('close', (event) => {
				console.debug('[websocket] connection closed', event);
			});

			ws.addEventListener('message', (event) => {
				if (viewMode !== ViewMode.Streaming) return;

				const data = JSON.parse(event.data);

				const processTaxi = (taxi: TaxiAvailability) => {
					if (
						cache_availability_stream.length > 0 &&
						cache_availability_stream[0]?.b_id != taxi.b_id
					) {
						const oldid = cache_availability_stream[0].b_id;
						const newid = taxi.b_id;
						cache_availability_stream = []; // reset on new batch
						console.log('Reset due to new batch - Old Id: ', oldid, ' New Id: ', newid);
					}

					cache_availability_stream.push(taxi);
					next(null);
				};

				if (Array.isArray(data)) {
					data.forEach((t) => {
						processTaxi(t);
					});
				} else {
					processTaxi(data);
				}
			});
		}
	});

	onDestroy(() => {
		complete();
	});

	$: if (useTimeline) {
		viewMode = ViewMode.Timeline;
		next(null);
	} else {
		viewMode = ViewMode.Streaming;
		next(null);
	}

	let playInterval: NodeJS.Timeout;

	$: if (time !== -1) {
		next(null);
	}

	$: if (noOfClusters !== -1) {
		next(null);
	}
</script>

<div class="h-screen w-screen" id="map"></div>
{#if selectedTaxi}
	<div class="fixed left-3 top-3 bg-slate-500 rounded-md p-4 opacity-70">
		<div class="grid grid-cols-2 gap-1 text-white">
			<div>Batch ID:</div>
			<div>{selectedTaxi.b_id}</div>
			<div>Longitude:</div>
			<div>{selectedTaxi.lon}</div>
			<div>Latitude:</div>
			<div>{selectedTaxi.lat}</div>
			<div>Created At:</div>
			<div>{dayjs.utc(selectedTaxi.created_at).tz('Singapore').format('HHmm - DD/MM/YYYY')}</div>
		</div>
	</div>
{/if}
<div
	class="fixed left-3 bottom-3 p-4 bg-slate-500 text-white rounded-md flex flex-col justify-center items-start
        gap-3 shadow-md w-48 z-10"
>
	<button
		class="p-2 bg-slate-400 rounded-md hover:brightness-110 active:brightness-125 w-full"
		class:bg-orange-300={layerVisibility.scatter}
		class:bg-slate-400={!layerVisibility.scatter}
		on:click={() => {
			for (let key in layerVisibility) {
				layerVisibility[key] = false;
			}

			layerVisibility.scatter = true;
			layerVisibility = layerVisibility;
			next(null);
		}}>Scatter Plot</button
	>
	<button
		class="p-2 rounded-md hover:brightness-110 active:brightness-125 w-full"
		class:bg-orange-300={layerVisibility.heatmap}
		class:bg-slate-400={!layerVisibility.heatmap}
		on:click={() => {
			for (let key in layerVisibility) {
				layerVisibility[key] = false;
			}

			layerVisibility.heatmap = true;
			next(null);
		}}>Heatmap</button
	>
	<div class="flex flex-col gap-1 p-3 w-full bg-slate-800 rounded-md">
		<button
			class="p-2 rounded-md hover:brightness-110 active:brightness-125 w-full"
			class:bg-orange-300={layerVisibility.cluster}
			class:bg-slate-400={!layerVisibility.cluster}
			on:click={() => {
				for (let key in layerVisibility) {
					layerVisibility[key] = false;
				}

				layerVisibility.cluster = true;
				next(null);
			}}>Cluster</button
		>
		<div class="flex gap-2 p-1">
			<input class="w-full" type="range" min="2" max="50" bind:value={noOfClusters} />
			{noOfClusters}
		</div>
	</div>

	<label class="inline-flex items-center cursor-pointer">
		<input type="checkbox" bind:checked={useTimeline} class="sr-only peer" />
		<div
			class="relative w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"
		></div>
		<span class="ms-3 text-sm font-medium text-gray-900 dark:text-gray-300">Use Timeline</span>
	</label>
</div>

{#if viewMode === ViewMode.Timeline}
	<div class="fixed bottom-8 w-full px-60 z-0">
		<div class="flex grow flex-col gap-2 bg-slate-500 rounded-md p-4 opacity-80">
			<input class="w-full" type="range" min="0" max="1439" bind:value={time} />
			<div class="flex gap-2 justify-start items-center">
				<div>
					<button
						on:click={() => {
							isPlaying = !isPlaying;

							if (isPlaying) {
								clearInterval(playInterval);
								playInterval = setInterval(() => {
									time = time + 1;
								}, 1000);
							} else {
								clearInterval(playInterval);
							}
						}}
						class="rounded-md text-white p-2 w-32 hover:brightness-110 active:brightness-125"
						class:bg-orange-300={isPlaying}
						class:bg-slate-400={!isPlaying}>{isPlaying ? 'PAUSE' : 'PLAY'}</button
					>
				</div>
				<div class="grid grid-cols-2 gap-2 grid-rows-2 text-white">
					<div>Data From:</div>
					<div>
						{dayjs()
							.subtract(dayjs.duration({ days: 1 }))
							.format('DD/MM/YYYY')}
					</div>
					<div>Time:</div>
					<div>
						{Math.floor(time / 60)
							.toString()
							.padStart(2, '0')}:{(time % 60).toString().padStart(2, '0')}
					</div>
				</div>
			</div>
		</div>
	</div>
{/if}
