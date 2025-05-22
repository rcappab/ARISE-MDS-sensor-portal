import React from "react";
import { Link } from "react-router-dom";
import { useObjectType } from "../../context/ObjectTypeCheck.tsx";

interface Props {
	selectedDataID: number;
	objectType: string;
}

const DetailDisplayRelated = ({ selectedDataID, objectType }: Props) => {
	const { validGalleries } = useObjectType();

	const getButtons = function () {
		return validGalleries.map((validType) => {
			return (
				<Link
					to={`/${objectType}s/${selectedDataID}/${validType}s`}
					key={validType}
					className="p-2 flex-fill"
				>
					<button className="btn btn-primary w-100">Show {validType}s</button>
				</Link>
			);
		});
	};

	return <div className="d-flex justify-content-evenly">{getButtons()}</div>;
};

export default DetailDisplayRelated;
