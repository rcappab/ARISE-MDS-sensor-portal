import React from "react";
import GalleryTile from "./GalleryTile.tsx";

interface Props {
	data: [];
	onTileClick: (index) => void;
	nameKey: string;
}

const GalleryDisplay = ({
	nameKey,
	data = [],
	onTileClick = () => {},
}: Props) => {
	return (
		<div
			id="gallery-rows"
			className="row row-cols-1 row-cols-lg-5 justify-content-center justify-content-lg-start"
		>
			{data.map((x, index) => {
				return (
					<GalleryTile
						cardTitle={x[nameKey]}
						index={index}
						key={`tile_${index}`}
						extraClasses={x["is_active"] ? "" : "text-white bg-secondary"}
						onClick={onTileClick}
					/>
				);
			})}
		</div>
	);
};

export default GalleryDisplay;
