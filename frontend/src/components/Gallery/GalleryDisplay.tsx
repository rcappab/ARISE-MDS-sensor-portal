import React, { useState } from "react";

import { useOutletContext } from "react-router-dom";
import GalleryTileDisplay from "./GalleryTileDisplay.tsx";
import GalleryTableDisplay from "./GalleryTableDisplay.tsx";

interface Props {
	objectType: string;
	data: [];
	tableMode: boolean;
	onTileClick: (index) => void;
}

const GalleryDisplay = ({
	objectType,
	data = [],
	tableMode = false,
	onTileClick = () => {},
}: Props) => {
	const { nameKey } = useOutletContext();

	return tableMode ? (
		<GalleryTableDisplay
			objectType={objectType}
			data={data}
			onRowClick={onTileClick}
		/>
	) : (
		<GalleryTileDisplay
			objectType={objectType}
			data={data}
			onTileClick={onTileClick}
		/>
	);
};

export default GalleryDisplay;
