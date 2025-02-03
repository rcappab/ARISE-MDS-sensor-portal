import React from "react";
import GalleryTile from "./GalleryTile.tsx";
import { useOutletContext } from "react-router-dom";

interface Props {
	objectType: string;
	data: [];
	onTileClick: (index) => void;
}

const GalleryDisplay = ({
	objectType,
	data = [],
	onTileClick = () => {},
}: Props) => {
	const { nameKey } = useOutletContext();
	let thumbKey = "";
	let textKey = "";
	if (objectType === "deployment") {
		thumbKey = "last_imageURL";
		textKey = "site";
	} else if (objectType === "datafile") {
		thumbKey = "file_url";
		textKey = "recording_dt";
	}

	return (
		<div
			id="gallery-rows"
			className="row row-cols-1 row-cols-lg-5 justify-content-center justify-content-start"
		>
			{data.map((x, index) => {
				let imageURL = x[thumbKey];
				if (objectType === "datafile") {
					console.log(x["file_format"]);
					if (
						![".jpg", ".jpeg", ".png"].includes(
							String(x["file_format"]).toLowerCase()
						)
					) {
						imageURL = "";
					}
				}

				let extraClasses = "";
				if (objectType !== "datafile") {
					x["is_active"]
						? (extraClasses = "")
						: (extraClasses = "text-white bg-secondary");
				}
				return (
					<GalleryTile
						cardTitle={x[nameKey]}
						cardText={x[textKey]}
						cardImageURL={imageURL}
						index={index}
						key={`tile_${index}`}
						extraClasses={extraClasses}
						onClick={onTileClick}
					/>
				);
			})}
		</div>
	);
};

export default GalleryDisplay;
