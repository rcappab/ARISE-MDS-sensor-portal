import React, { useState } from "react";
import "../../../styles/observationform.css";

interface ObservationTableRowProps {
	obsDataRow: object;
	index: number;
	onRowHover: (index: number) => void;
}

const ObservationTableRow = ({
	obsDataRow,
	index,
	onRowHover,
}: ObservationTableRowProps) => {
	const [rowHover, setRowHover] = useState(false);

	const handleRowHover = (hover) => {
		onRowHover(hover ? index : -1);
		setRowHover(hover);
	};

	return (
		<tr
			onMouseEnter={() => handleRowHover(true)}
			onMouseLeave={() => handleRowHover(false)}
			className={
				rowHover
					? "highlight"
					: obsDataRow["validation_requested"]
					? "uncertain"
					: ""
			}
		>
			<td>{obsDataRow["obs_dt"]}</td>
			<td>{`${obsDataRow["number"]} ${obsDataRow["species_name"]}`}</td>
			<td>{obsDataRow["species_common_name"]}</td>
			<td>{obsDataRow["source"]}</td>
			<td>{obsDataRow["annotated_by"]}</td>
			<td>{obsDataRow["sex"]}</td>
			<td>{obsDataRow["lifestage"]}</td>
			<td>{obsDataRow["behaviour"]}</td>
		</tr>
	);
};

interface ObservationTableProps {
	allObsData: object[] | [];
	onRowHover: (index: number) => void;
}

const ObservationTable = ({
	allObsData = [],
	onRowHover = (index) => {},
}: ObservationTableProps) => {
	const getObsRows = function (obsDataRow, index) {
		return (
			<ObservationTableRow
				key={index}
				obsDataRow={obsDataRow}
				index={index}
				onRowHover={onRowHover}
			/>
		);
	};

	if (allObsData.length === 0) {
		return null;
	}

	return (
		<table className="table table-sm">
			<thead>
				<tr key="table-head">
					<td>Date time</td>
					<td>Species</td>
					<td>Common name</td>
					<td>Source</td>
					<td>Annotated by</td>
					<td>Sex</td>
					<td>Lifestage</td>
					<td>Behaviour</td>
				</tr>
			</thead>
			<tbody>
				{allObsData.map((obsData, index) => {
					return getObsRows(obsData, index);
				})}
			</tbody>
		</table>
	);
};

export default ObservationTable;
