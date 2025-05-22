import React from "react";
import GalleryTile from "./GalleryTile.tsx";
import { useObjectType } from "../../context/ObjectTypeCheck.tsx";

interface Props {
	objectType: string;
	data: [];
	onClick?: (e: React.MouseEvent<Element, MouseEvent>, index: number) => void;
	selectedIndexes: number[];
}

const GalleryTileDisplay = ({
	objectType,
	data = [],
	onClick = (e, index) => {},
	selectedIndexes,
}: Props) => {
	const { nameKey } = useObjectType();
	let thumbKey = "";
	let textKey = "";
	if (objectType === "deployment") {
		thumbKey = "thumb_url";
		textKey = "site";
	} else if (objectType === "datafile") {
		thumbKey = "thumb_url";
		textKey = "recording_dt";
	} else if (objectType === "device") {
		textKey = "type";
	}

	return (
		<div
			id="gallery-rows"
			className="row row-cols-1 row-cols-lg-5 justify-content-start g-2 p-2"
		>
			{data.map((x, index) => {
				let imageURL = x[thumbKey];
				let extraClasses = "";
				if (objectType !== "datafile") {
					x["is_active"]
						? (extraClasses = "")
						: (extraClasses = "text-white bg-secondary");
				}
				return (
					<div
						className="col "
						key={`tile_div_${index}`}
					>
						<GalleryTile
							cardTitle={x[nameKey]}
							cardText={x[textKey]}
							cardImageURL={imageURL}
							index={index}
							key={`tile_${index}`}
							extraClasses={
								selectedIndexes.includes(index)
									? extraClasses + "selected"
									: extraClasses
							}
							onClick={(e) => onClick(e, index)}
						/>
					</div>
				);
			})}
		</div>
	);
};

export default GalleryTileDisplay;
