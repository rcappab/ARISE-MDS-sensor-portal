import React, { useState, useEffect } from "react";
import {
	MapContainer,
	TileLayer,
	Marker,
	Popup,
	useMap,
	useMapEvent,
} from "react-leaflet";
import { Icon } from "leaflet";

interface Props {
	readOnly: boolean;
	formLatLong: { lat: number; lng: number } | null;
	handleChangeLatLong: () => {};
}

const FormMapMarker = ({
	readOnly = false,
	formLatLong = null,
	handleChangeLatLong = () => {},
}: Props) => {
	const defaultIcon = new Icon({
		iconUrl:
			"https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
		iconSize: [25, 41],
		iconAnchor: [12, 41],
		popupAnchor: [1, -34],
		shadowSize: [41, 41],
	});

	//const [mapLocation, setMapLocation] = useState(
	//	formLatLong ? formLatLong : null
	//);
	let mapLocation = formLatLong ? formLatLong : null;

	const map = useMap();

	useEffect(() => {
		if (mapLocation == null) {
			// map.locate().on("locationfound", function (e) {
			// 	//setMapLocation(e.latlng);
			// 	mapLocation = e.latlng;
			// 	handleChangeLatLong(e.latlng);
			// 	map.setView(e.latlng, 10);
			// });
		} else {
			map.setView(mapLocation, 10);
		}
	}, [map]);


	const mapLocate = useMapEvent("locationfound", (e) => {
		if (mapLocation == null) {
			mapLocation = e.latlng;
			handleChangeLatLong(e.latlng);
			map.setView(e.latlng, 10);
		}
	});

	const mapClick = useMapEvent("click", (e) => {
		if (!readOnly) {
			map.setView(e.latlng, map.getZoom());
			handleChangeLatLong(e.latlng);
			//setMapLocation(e.latlng);
			mapLocation = e.latlng;
		}
	});

	console.log(formLatLong ? true : false);
	console.log(formLatLong);
	console.log(mapLocation);

	return mapLocation === null ? null : (
		<Marker
			position={mapLocation}
			icon={defaultIcon}
			interactive={false}
		></Marker>
	);
};

export default FormMapMarker;
