import React, { useState } from "react";
import { dtFormat } from "../../utils/timezoneFunctions";
import "../../styles/galleryTable.css";
import { useObjectType } from "../../context/ObjectTypeCheck.tsx";

interface Props {
	objectType: string;
	data: [];
	onClick: (e: React.MouseEvent<Element, MouseEvent>, index: number) => void;
	selectedIndexes: number[];
}

const GalleryTableDisplay = ({
	objectType,
	data = [],
	onClick = (e, index) => {},
	selectedIndexes,
}: Props) => {
	const { nameKey } = useObjectType();
	const [sortConfig, setSortConfig] = useState<{
		key: string;
		direction: "asc" | "desc";
	} | null>(null);
	const [hoveredRow, setHoveredRow] = useState<number | null>(null);

	let columnHeaders = [] as string[];
	let timeKeys = [] as string[];
	if (objectType === "deployment") {
		columnHeaders = [
			"site",
			"deployment_ID",
			"device_type",
			"device",
			"deployment_start",
		];
		timeKeys = ["deployment_start"];
	} else if (objectType === "datafile") {
		columnHeaders = [nameKey, "deployment", "recording_dt", "thumb_url"];
		timeKeys = ["recording_dt"];
	} else if (objectType === "device") {
		columnHeaders = [nameKey, "name", "type", "model", "created_on"];
		timeKeys = ["created_on"];
	} else if (objectType === "project") {
		columnHeaders = [nameKey, "project_ID", "organisation", "created_on"];
		timeKeys = ["created_on"];
	}

	const sortedData = React.useMemo(() => {
		if (!sortConfig) return data;

		return [...data].sort((a, b) => {
			const aValue = a[sortConfig.key];
			const bValue = b[sortConfig.key];

			if (aValue < bValue) return sortConfig.direction === "asc" ? -1 : 1;
			if (aValue > bValue) return sortConfig.direction === "asc" ? 1 : -1;
			return 0;
		});
	}, [data, sortConfig]);

	const convertDates = function (key, value) {
		if (timeKeys.includes(key)) {
			let currentTime = value;

			let dateTime = new Date(currentTime);
			return dtFormat.format(dateTime);
		} else {
			return value;
		}
	};

	const handleSort = (key: string) => {
		setSortConfig((prevConfig) => {
			if (prevConfig?.key === key) {
				return {
					key,
					direction: prevConfig.direction === "asc" ? "desc" : "asc",
				};
			}
			return { key, direction: "asc" };
		});
	};

	return (
		<table className="table table-hover mt-2">
			<thead className="table-dark">
				<tr>
					{columnHeaders
						.filter((header) => header !== "thumb_url")
						.map((header, index) => (
							<th
								key={`header_${index}`}
								onClick={() => handleSort(header)}
								style={{ cursor: "pointer" }}
							>
								{header}{" "}
								{sortConfig?.key === header
									? sortConfig.direction === "asc"
										? "▲"
										: "▼"
									: ""}
							</th>
						))}
					{columnHeaders.includes("thumb_url") && <th>Thumbnail</th>}
				</tr>
			</thead>
			<tbody>
				{sortedData.map((x, index) => {
					let imageURL = x["thumb_url"];
					let extraClasses = "";
					if (objectType !== "datafile") {
						x["is_active"]
							? (extraClasses = "")
							: (extraClasses = "text-white bg-secondary");
					}
					if (hoveredRow === index || selectedIndexes.includes(index)) {
						extraClasses += "table-hover";
					}
					return (
						<tr
							key={`row_${index}`}
							className={extraClasses}
							onClick={(e) => onClick(e, index)}
							onMouseEnter={() => setHoveredRow(index)}
							onMouseLeave={() => setHoveredRow(null)}
							style={{ cursor: "pointer" }}
						>
							{columnHeaders
								.filter((header) => header !== "thumb_url")
								.map((header, colIndex) => (
									<td key={`col_${colIndex}`}>
										{convertDates(header, x[header])}
									</td>
								))}
							{columnHeaders.includes("thumb_url") && (
								<td>
									{imageURL ? (
										<img
											src={imageURL}
											alt="Thumbnail"
											style={{ width: "100%", height: "100%" }}
										/>
									) : null}
								</td>
							)}
						</tr>
					);
				})}
			</tbody>
		</table>
	);
};

export default GalleryTableDisplay;
