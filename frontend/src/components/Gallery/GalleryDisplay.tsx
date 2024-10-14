import React from "react";
import GalleryTile from "./GalleryTile.tsx";

interface Props {
	data: [];
	onTileClick: (index) => void;
}

const GalleryDisplay = ({ data = [], onTileClick = () => {} }: Props) => {
	return (
		<div
			id="gallery-rows"
			className="row row-cols-1 row-cols-md-2"
		>
			{data.map((x, index) => {
				return (
					<GalleryTile
						cardTitle={x["deployment_deviceID"]}
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
