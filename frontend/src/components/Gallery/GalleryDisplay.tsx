import React from "react";
import GalleryTileDisplay from "./GalleryTileDisplay.tsx";
import GalleryTableDisplay from "./GalleryTableDisplay.tsx";

interface Props {
	objectType: string | undefined;
	data: [];
	tableMode: boolean;
	onClick: (e: React.MouseEvent<Element, MouseEvent>, index: number) => void;
	selectedIndexes: number[];
	nameKey: string;
}

const GalleryDisplay = ({
	objectType,
	data = [],
	tableMode = false,
	onClick = (e, index) => {},
	selectedIndexes,
	nameKey,
}: Props) => {
	if (objectType === undefined) {
		return null;
	}

	return tableMode ? (
		<GalleryTableDisplay
			objectType={objectType}
			data={data}
			onClick={onClick}
			selectedIndexes={selectedIndexes}
			nameKey={nameKey}
		/>
	) : (
		<GalleryTileDisplay
			objectType={objectType}
			data={data}
			onClick={onClick}
			selectedIndexes={selectedIndexes}
			nameKey={nameKey}
		/>
	);
};

export default GalleryDisplay;
