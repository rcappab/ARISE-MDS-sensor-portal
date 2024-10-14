import React, { useRef, useEffect } from "react";
import { Marker, useMap, useMapEvent } from "react-leaflet";
import { Icon, DomEvent } from "leaflet";

interface Props {
	handleChangeLatLong: (e) => void;
}

const ResetLocation = ({ handleChangeLatLong = (e) => {} }: Props) => {
	const ref = useRef(null);

	useEffect(() => {
		if (ref.current) {
			DomEvent.disableClickPropagation(ref.current);
		}
	});

	const map = useMap();

	const resetLocation = function (e) {
		handleChangeLatLong(e.latlng);
		map.locate();
	};

	return (
		<button
			type="button"
			ref={ref}
			onClick={resetLocation}
			className="btn reset-location-button btn-danger btn-lg"
		>
			Reset location
		</button>
	);
};

export default ResetLocation;
