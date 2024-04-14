"use client";

import Map from "react-map-gl";
import "mapbox-gl/dist/mapbox-gl.css";

import classes from "./page.module.css";

export default function Home() {
	const mapboxToken = process.env.NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN;
  console.log(mapboxToken);

	return (
		<main className={classes.mainStyle}>
			<Map
				mapboxAccessToken={mapboxToken}
				mapStyle="mapbox://styles/mapbox/standard"
        // mapStyle="mapbox://styles/mapbox/navigation-night-v1"
				style={classes.mapStyle}
				initialViewState={{ latitude: 35.668641, longitude: 139.750567, zoom: 10 }}
				maxZoom={20}
				minZoom={3}
        pitch = {45}
			></Map>
		</main>
	);
}
