import React, { useCallback, useContext, useState } from "react";
import { Link } from "react-router-dom";
import RectDraw from "./Observations/RectDraw.tsx";
import FavouriteButton from "./FavouriteButton.tsx";
import { ObsEditModeContext } from "../../context/ObsModeContext.jsx";
import AuthContext from "../../context/AuthContext.jsx";
import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { getData } from "../../utils/FetchFunctions.js";
import Loading from "../General/Loading.tsx";
import ObservationForm, {
	obsDataType,
} from "./Observations/ObservationForm.tsx";
import ObservationTable from "./Observations/ObservationTable.tsx";
import { Tab, TabList, TabPanel, Tabs } from "react-tabs";
import Audio from "../General/Audio.tsx";

interface LinkedFileProps {
	linkedFileData: object;
}

const DetailDisplayLinkedFiles = ({ linkedFileData }: LinkedFileProps) => {
	const getTabs = function () {
		const tabs = Object.keys(linkedFileData).map((key) => {
			return <Tab>{key}</Tab>;
		});
		return tabs;
	};

	const getTabContent = function () {
		const tabContent = Object.keys(linkedFileData).map((key) => {
			return (
				<TabPanel>
					<div>
						<img
							src={"/" + linkedFileData[key]["url"]}
							alt={key}
							style={{
								objectFit: "contain",
								width: "100%",
								maxHeight: "30rem",
								userSelect: "none",
							}}
						/>
					</div>
				</TabPanel>
			);
		});
		return tabContent;
	};

	return (
		<Tabs>
			<TabList>{getTabs()}</TabList>
			{getTabContent()}
		</Tabs>
	);
};

interface Props {
	fileData: Object;
}

const DetailDisplayFile = ({ fileData }: Props) => {
	const { authTokens, user } = useContext(AuthContext);
	const { obsEditMode, setObsEditMode } = useContext(ObsEditModeContext);

	const isImage = [".jpg", ".jpeg", ".png"].includes(
		fileData["file_format"].toLowerCase()
	);
	const isAudio = [".mp3", ".wav"].includes(
		fileData["file_format"].toLowerCase()
	);
	const isLocal = fileData["file_url"];
	const hasLinkedFiles =
		fileData["linked_files"] !== undefined &&
		Object.keys(fileData["linked_files"]).length > 0;
	const fileURL = "/" + fileData["file_url"];
	const canAnnotate = fileData["can_annotate"];

	const [bboxEditMode, setBboxEditMode] = useState({
		edit: false,
		index: -1,
	});
	const [tempObsData, setTempObsData] = useState<obsDataType[]>([]);
	const [hoverIndex, setHoverIndex] = useState(-1);
	const [expanded, setExpanded] = useState(false);

	const handleObservationEdit = useCallback((rowData, newRow = false) => {
		if (newRow) {
			setTempObsData((prevState) => {
				return [...prevState, rowData];
			});
		} else {
			setTempObsData((prevState) => {
				return prevState.map((x, i) => {
					if (i === rowData.index) {
						return rowData;
					} else {
						return x;
					}
				});
			});
		}
	}, []);

	const handleStartEditBoundingBox = useCallback((index) => {
		setBboxEditMode({
			edit: true,
			index: index,
		});
	}, []);

	const handleStopEditBoundingBox = useCallback((newObsData) => {
		setBboxEditMode({
			edit: false,
			index: -1,
		});
		setTempObsData(newObsData);
	}, []);

	const getDataFunc = async () => {
		let apiURL = `datafile/${fileData["id"]}/observations/`;
		let response_json = await getData(apiURL, authTokens.access);
		let obs_json = response_json.results;
		setTempObsData(obs_json);
		return obs_json;
	};

	const {
		isLoading,
		//isError,
		isPending,
		data,
		//error,
		isRefetching,
		//isPlaceholderData,
		refetch,
	} = useQuery({
		queryKey: ["obs", user, fileData["id"]],
		queryFn: () => getDataFunc(),
		placeholderData: keepPreviousData,
		refetchOnWindowFocus: false,
	});

	const handleSetEditMode = useCallback(
		(startEdit) => {
			if (!startEdit) {
				refetch();
			}
			setTempObsData(data);
			setObsEditMode(startEdit);
		},
		[data, refetch, setObsEditMode]
	);

	const handleRowHover = useCallback((index) => {
		setHoverIndex(index);
	}, []);

	const getObsTable = () => {
		if (isLoading || isPending || isRefetching) {
			return (
				<>
					<div className="row w-100"></div>
					<div className="row w-100">
						<Loading />
					</div>
				</>
			);
		} else {
			return (
				<div>
					{obsEditMode ? (
						<ObservationForm
							allObsData={tempObsData}
							fileData={fileData}
							onSubmit={refetch}
							onEditBoundingBox={handleStartEditBoundingBox}
							onEdit={handleObservationEdit}
							onHover={handleRowHover}
							onStopEdit={() => handleSetEditMode(false)}
						/>
					) : (
						<ObservationTable
							allObsData={data}
							onRowHover={handleRowHover}
						/>
					)}
					{canAnnotate ? (
						<div className="col">
							<button
								className={`btn ${
									obsEditMode
										? "btn-outline-danger"
										: "btn-outline-primary w-100"
								}`}
								onClick={() => {
									handleSetEditMode(!obsEditMode);
								}}
							>
								{obsEditMode ? "Cancel annotating" : "Start annotating"}
							</button>
						</div>
					) : null}
				</div>
			);
		}
	};

	return (
		<div>
			{isLocal && (
				<div
					className="mb-2"
					onClick={() => {
						if (isImage && !obsEditMode) {
							setExpanded(!expanded);
						}
					}}
				>
					{hasLinkedFiles && (
						<DetailDisplayLinkedFiles
							linkedFileData={fileData["linked_files"]}
						/>
					)}
					{isImage && (
						<div className={"rectdraw-container"}>
							<img
								src={fileURL}
								alt={fileData["file_name"]}
								style={{
									objectFit: "contain",
									width: "100%",
									maxHeight: expanded ? "100%" : "30rem",
									userSelect: "none",
								}}
							/>
							<RectDraw
								obsData={tempObsData}
								editMode={bboxEditMode.edit}
								editIndex={bboxEditMode.index}
								onFinishEditing={handleStopEditBoundingBox}
								hoverIndex={hoverIndex}
							/>
						</div>
					)}
					{isAudio && (
						<div>
							<Audio src={fileURL} />
						</div>
					)}
				</div>
			)}

			<div className="row p-2">
				{isLocal && (
					<div className="col mb-2">
						<Link
							to={fileURL}
							target="_blank"
							download
						>
							<button className={"btn btn-outline-primary w-100 h-100"}>
								Download File
							</button>
						</Link>
					</div>
				)}
				<div className="col mb-2">
					<FavouriteButton
						id={fileData["id"]}
						favourite={fileData["favourite"]}
					/>
				</div>
				{obsEditMode && <div className="row w-100"></div>}
				{getObsTable()}
			</div>
		</div>
	);
};

export default DetailDisplayFile;
