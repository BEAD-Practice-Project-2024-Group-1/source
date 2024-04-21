<script lang="ts" context="module">
	import type { LngLatLike, LngLatBoundsLike, IControl } from 'maplibre-gl';
	import { MapboxOverlay as DeckOverlay } from '@deck.gl/mapbox';
	import { ScatterplotLayer, GeoJsonLayer } from '@deck.gl/layers';
	import { HeatmapLayer } from '@deck.gl/aggregation-layers';
	import 'maplibre-gl/dist/maplibre-gl.css';
	import { onDestroy, onMount } from 'svelte';
	import { pipe, debounce, makeSubject, subscribe } from 'wonka';
	import type { Feature, GeoJSON } from 'geojson';

	const SINGAPORE_SOUTHWEST_LNLGAT: LngLatLike = [103.51461, 1.099306];
	const SINGAPORE_NORTHEAST_LNLGAT: LngLatLike = [104.162353, 1.587878];
	const MAX_BOUNDS: LngLatBoundsLike = [SINGAPORE_SOUTHWEST_LNLGAT, SINGAPORE_NORTHEAST_LNLGAT];

	export type TaxiAvailability = {
		b_id: string;
		lon: number;
		lat: number;
	};
</script>

<script lang="ts">
	export let planning_areas: Array<Feature> = [];

	let webSocketEstablished = false;
	let ws: WebSocket | null = null;

	let taxAvailability: Array<TaxiAvailability> = [];
	let selectedTaxi: TaxiAvailability;
	let layerVisibility: Record<string, boolean> = {
		scatter: true,
		heatmap: false
	};

	let subject = makeSubject();
	let { source, next, complete } = subject;

	const updateDeck = (deck: DeckOverlay) => {
		deck.setProps({
			layers: [
				new GeoJsonLayer({
					id: 'planning-area-geojson',
					visible: true,
					data: planning_areas,
					getFillColor: [0, 100, 100, 100],
					getText: (d: Feature) => d.id,
					getLineWidth: 20,
					stroked: true,
					pickable: true
				}),
				new ScatterplotLayer<TaxiAvailability>({
					id: 'taxi-scatterplot',
					data: taxAvailability,
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
				new HeatmapLayer<TaxiAvailability>({
					id: 'taxi-heatmap',
					visible: layerVisibility.heatmap,
					data: taxAvailability,
					aggregation: 'SUM',
					getPosition: (d: TaxiAvailability) => [d.lon, d.lat],
					getWeight: (d) => 1,
					radiusPixels: 25
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
			const deckOverlay = new DeckOverlay({});

			map.addControl(deckOverlay as IControl);
			map.addControl(new maplibregl.NavigationControl());

			pipe(
				source,
				debounce(() => 1000),
				subscribe(() => {
					updateDeck(deckOverlay);
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
				const data = JSON.parse(event.data);

				const processTaxi = (taxi: TaxiAvailability) => {
					if (taxAvailability.length > 0 && taxAvailability[0]?.b_id != taxi.b_id) {
						const oldid = taxAvailability[0].b_id;
						const newid = taxi.b_id;
						taxAvailability = []; // reset on new batch
						console.log('Reset due to new batch - Old Id: ', oldid, ' New Id: ', newid);
					}

					taxAvailability.push(taxi);
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
		</div>
	</div>
{/if}
<div
	class="fixed left-3 bottom-3 p-4 bg-slate-500 text-white rounded-md flex flex-col justify-center items-start
        gap-3 shadow-md"
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
</div>
