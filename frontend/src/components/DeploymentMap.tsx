import React, { useCallback, useEffect, useRef, useState } from "react";
import {
	FeatureGroup,
	LayerGroup,
	MapContainer,
	Marker,
	Popup,
	TileLayer,
} from "react-leaflet";
import UserLocationMarker from "./MapUserLocationMarker.tsx";
import ResetLocation from "./MapControlResetLocation.tsx";
import { Icon } from "leaflet";

interface Props {
	deployments: [{ latitude; longitude; deployment_device_ID }];
}

const DeploymentMap = ({ deployments }: Props) => {
	const defaultIcon = new Icon({
		iconUrl:
			"https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
		iconSize: [25, 41],
		iconAnchor: [12, 41],
		popupAnchor: [1, -34],
		shadowSize: [41, 41],
	});

	const featureGroupRef = useRef();
	const [map, setMap] = useState(null);

	const setBounds = useCallback(() => {
		if (!map) return;
		console.log(map);
		let newBounds = featureGroupRef.current.getBounds();
		map.fitBounds(newBounds);
	}, [map]);

	useEffect(() => {
		setBounds();
	}, [map, setBounds]);

	return (
		<div>
			<MapContainer
				center={[0, 0]}
				zoom={1}
				scrollWheelZoom={false}
				style={{ height: "75vh", width: "100%" }}
				whenReady={(e) => setMap(e.target)}
			>
				<TileLayer
					attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
					url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
				/>
				<FeatureGroup ref={featureGroupRef}>
					{deployments.map((deploymentData) => {
						let latLng = {
							lat: deploymentData.latitude,
							lng: deploymentData.longitude,
						};
						return (
							<Marker
								position={latLng}
								icon={defaultIcon}
							>
								<Popup>{deploymentData.deployment_device_ID}</Popup>
							</Marker>
						);
					})}
				</FeatureGroup>
				<UserLocationMarker />
				<ResetLocation
					handleChangeLatLong={(e) => {
						setBounds();
					}}
				/>
			</MapContainer>
		</div>
	);
};

export default DeploymentMap;
