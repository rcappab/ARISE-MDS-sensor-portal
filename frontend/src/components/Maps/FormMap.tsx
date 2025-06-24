import { MapContainer, TileLayer } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import FormMapMarker from "./FormMapMarker.tsx";
import UserLocationMarker from "./MapUserLocationMarker.tsx";
import ResetLocation from "./MapControlResetLocation.tsx";
import "../../styles/map.css";
import React from "react";

interface Props {
	latitude: number | null;
	longitude: number | null;
	handleChangeLatLong: (e) => void;
}

const FormMap = ({
	latitude = null,
	longitude = null,
	handleChangeLatLong = (e) => {},
}: Props) => {
	return (
		<div>
			<MapContainer
				center={[0, 0]}
				zoom={10}
				scrollWheelZoom={false}
				style={{ height: "20vh", width: "100%" }}
			>
				<TileLayer
					attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
					url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
				/>
				<UserLocationMarker />
				<FormMapMarker
					formLatLong={latitude ? { lat: latitude, lng: longitude } : null}
					handleChangeLatLong={handleChangeLatLong}
				/>
				<div className="leaflet-bottom leaflet-left">
					<div className="leaflet-control">
						<ResetLocation
							handleChangeLatLong={() => {
								handleChangeLatLong(null);
							}}
						/>
					</div>
				</div>
			</MapContainer>
		</div>
	);
};

export default FormMap;
