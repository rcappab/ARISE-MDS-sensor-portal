import React from "react";
import DetailDisplayTable from "./DetailDisplayTable.tsx";
import DetailEdit from "./DetailEdit.tsx";
import DetailDisplayRelated from "./DetailDisplayRelated.tsx";

interface Props {
	objectType: string;
	editMode: boolean;
	selectedData: object | null;
	onSubmit?: (e: Event, addNew: boolean, response: object) => void;
	onCancel?: (e: any) => void;
	hideKeys?: string[];
	timeKeys?: string[];
	jsonKeys?: string[];
}

const DetailModalContent = ({
	objectType,
	editMode,
	selectedData,
	onSubmit = (e, addNew, response) => {},
	onCancel = () => {},
	hideKeys = ["combo_project", "last_imageURL"],
	timeKeys = [
		"created_on",
		"modified_on",
		"recording_dt",
		"deploymentStart",
		"deploymentEnd",
	],
	jsonKeys = ["extra_info"],
}: Props) => {
	return editMode ? (
		<DetailEdit
			objectType={objectType}
			selectedData={selectedData}
			onSubmit={onSubmit}
			onCancel={onCancel}
		/>
	) : (
		<div>
			<DetailDisplayRelated
				objectType={objectType}
				selectedDataID={selectedData["id"] as number}
			/>
			<DetailDisplayTable
				selectedData={selectedData}
				hideKeys={hideKeys}
				timeKeys={timeKeys}
				jsonKeys={jsonKeys}
			/>
		</div>
	);
};

export default DetailModalContent;
