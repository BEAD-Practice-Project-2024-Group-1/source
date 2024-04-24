<script lang="ts" context="module">
	import Map from '$lib/Map/index.svelte';
	import type { PageData } from './$types';
</script>

<script lang="ts">
	export let data: PageData;
</script>

<Map planning_areas={data.planning_areas} full_day_taxi_availability={data.taxi_availability} />
