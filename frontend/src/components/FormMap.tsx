import React, { useState, UseEffect } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import { Icon } from "leaflet";
import "leaflet/dist/leaflet.css";
import FormMapMarker from "./FormMapMarker.tsx";
import UserLocationMarker from "./UserLocationMarker.tsx";

const FormMap = () => {
	const [latitude, setLatitude] = useState();
	const [longitude, setLongitude] = useState();

	const setLatLong = function (latlong) {
		console.log(latlong);
		setLatitude(Number(latlong.lat.toPrecision(8)));
		setLongitude(Number(latlong.lng.toPrecision(8)));
	};

	return (
		<div>
			<div className="row">
				<div className="form-floating col">
					<input
						name="Latitude"
						id="post-latitude"
						type="number"
						className="form-control"
						value={latitude}
						onChange={(e) => {
							setLatLong({
								lat: Number(e.target.value).toPrecision(8),
								lng: longitude,
							});
						}}
					/>
					<label htmlFor="post-latitude">Latitude</label>
				</div>
				<div className="form-floating col">
					<input
						name="Longitude"
						id="post-longitude"
						type="number"
						className="form-control"
						value={longitude}
						onChange={(e) => {
							setLatLong({
								lat: latitude,
								lng: Number(e.target.value).toPrecision(8),
							});
						}}
					/>
					<label htmlFor="post-longitiude">Longitude</label>
				</div>
			</div>

			<MapContainer
				center={[0, 0]}
				zoom={1}
				scrollWheelZoom={false}
				style={{ height: "100vh", width: "100%" }}
			>
				<TileLayer
					attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
					url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
				/>
				<UserLocationMarker />
				<FormMapMarker
					formLatLong={latitude ? { lat: latitude, lng: longitude } : null}
					handleChangeLatLong={setLatLong}
				/>
			</MapContainer>
		</div>
	);
};

export default FormMap;
