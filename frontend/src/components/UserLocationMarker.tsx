import React, { useState, useEffect } from "react";
import { useMap, Circle } from "react-leaflet";

const UserLocationMarker = () => {
	const [position, setPosition] = useState(null);
	const [radius, setRadius] = useState(null);

	const map = useMap();

	useEffect(() => {
		map.locate().on("locationfound", function (e) {
			console.log("location found");
			setPosition(e.latlng);
			setRadius(e.accuracy);
		});
	}, [map]);
	return position === null ? null : (
		<Circle
			center={position}
			radius={radius}
		/>
	);
};

export default UserLocationMarker;
