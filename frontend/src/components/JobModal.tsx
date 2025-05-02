import React, { useCallback, useContext, useState } from "react";
import { useSearchParams } from "react-router-dom";
import BasicModal from "./BasicModal.tsx";
import { useMutation, useQuery } from "@tanstack/react-query";
import AuthContext from "../context/AuthContext.jsx";
import { getData, postData } from "../utils/FetchFunctions.js";
import toast from "react-hot-toast";
import FormSelect from "./FormSelect.tsx";
import Loading from "./Loading.tsx";
import JSONInput from "./JSONInput.tsx";

interface jobDataEditorProps {
	jobName: string;
	objectType: string;
	queryData: object;
	jobData: object;
	onSetJobData: (object) => void;
	onChangeJobData: (key: string, value: any) => void;
}

const GenericJobData = ({
	jobName,
	objectType,
	queryData,
	jobData,
	onSetJobData,
	onChangeJobData,
}: jobDataEditorProps) => {
	return (
		<>
			<div>
				Do job {jobName} {queryData["object_n"]} {objectType}s
				{objectType === "datafile"
					? `of which 
				${queryData["archived_file_n"]} are archived. Total filesize
				${queryData["total_file_size"].toFixed(2)} GB.`
					: null}
				<br />
				This job has no specific front end implementation. Arguments can be
				provided using the editor below.
			</div>
			<div>
				<JSONInput
					name={"job_data_input"}
					onJSONchange={onSetJobData}
				/>
			</div>
		</>
	);
};

const DataBundleJobData = ({
	jobName,
	objectType,
	queryData,
	jobData,
	onSetJobData,
	onChangeJobData,
}: jobDataEditorProps) => {
	return (
		<>
			<div>
				Create data package of {queryData["object_n"]} files of which{" "}
				{queryData["archived_file_n"]} are archived. Total filesize{" "}
				{queryData["total_file_size"].toFixed(2)} GB.
			</div>
			<div className="row px-1 py-1 mb-3">
				<div className="col-lg-6">
					<FormSelect
						id="metadata_select"
						name="metadata_type"
						value={jobData["metadata_type"]}
						label="metadata type"
						choices={[
							{ value: "0", label: "Standard" },
							{ value: "1", label: "Camtrap DP" },
						]}
						isClearable={false}
						isSearchable={false}
						creatable={false}
						handleChange={(newValue) => {
							onChangeJobData("metadata_type", newValue);
						}}
					/>
				</div>
				<div className="form-check form-switch col-lg-4">
					<label htmlFor="includeFiles_checkbox">Include files</label>
					<input
						name="include_files"
						className="form-check-input form-control"
						id="includeFiles_checkbox"
						type="checkbox"
						checked={jobData["include_files"]}
						onChange={(e) => {
							onChangeJobData("include_files", e.target.checked);
						}}
					/>
				</div>
			</div>
		</>
	);
};

interface Props {
	jobName?: string;
	objectType?: string;
	show?: boolean;
	onClose?: () => void;
}

const JobModal = ({
	jobName = "",
	objectType = "datafile",
	show = false,
	onClose = () => {},
}: Props) => {
	const [searchParams, setSearchParams] = useSearchParams();
	const { user, authTokens } = useContext(AuthContext);

	const defaultJobData = useCallback(() => {
		let data = {};
		if (jobName === "create_data_package") {
			data["metadata_type"] = "0";
			data["include_files"] = true;
		}
		return data;
	}, [jobName]);

	const [jobData, setJobData] = useState(defaultJobData);
	//const jobName = "create_data_package";

	const setNewDataValue = useCallback(
		(key, value) => {
			const editedData = {
				...jobData,
				[key]: value,
			};
			console.log(editedData);
			setJobData(editedData);
		},
		[jobData]
	);

	const getDataFunc = async () => {
		let apiURL = `${objectType}/queryset_count/?${searchParams.toString()}`;
		let response_json = await getData(apiURL, authTokens.access);
		return response_json;
	};

	const { isLoading, isError, isPending, data, error, isPlaceholderData } =
		useQuery({
			queryKey: ["data", objectType, user, "count", searchParams.toString()],
			queryFn: () => getDataFunc(),
			enabled: show,
		});

	const newPOST = async function (x: { apiURL: string; data: object }) {
		let response_json = await postData(x.apiURL, authTokens.access, x.data);
		return response_json;
	};

	const doPost = useMutation({
		mutationFn: (inputValue: { apiURL: string; data: object }) =>
			newPOST(inputValue),
	});

	const startLoadingToast = () => {
		const toastId = toast.loading("Loading...");
		return toastId;
	};

	const onSubmit = async function (e) {
		e.preventDefault();
		let toastId = startLoadingToast();
		let response;
		response = await doPost.mutateAsync({
			apiURL: `${objectType}/start_job/${jobName}/?${searchParams.toString()}`,
			data: jobData,
		});
		if (!response["ok"]) {
			toast.error(
				`Error in submission ${
					response["detail"] ? ":" + response["detail"] : ""
				}`,
				{
					id: toastId,
				}
			);
		} else {
			toast.success(response["detail"], {
				id: toastId,
			});
		}
		onClose();
	};

	const getDataBundleEdit = () => {
		if (jobName === "create_data_package") {
			return (
				<DataBundleJobData
					jobName={jobName}
					objectType={objectType}
					queryData={data}
					jobData={jobData}
					onSetJobData={setJobData}
					onChangeJobData={setNewDataValue}
				/>
			);
		} else {
			return (
				<GenericJobData
					jobName={jobName}
					objectType={objectType}
					queryData={data}
					jobData={jobData}
					onSetJobData={setJobData}
					onChangeJobData={setNewDataValue}
				/>
			);
		}
	};

	return (
		<BasicModal
			modalShow={show}
			headerChildren={"Start job"}
		>
			{isLoading ? (
				<Loading />
			) : (
				<div>
					{getDataBundleEdit()}
					<div>
						<button
							type="button"
							className="btn btn-primary btn-lg ms-lg-2"
							onClick={onSubmit}
						>
							Start job
						</button>
						<button
							type="button"
							className="btn btn-danger btn-lg ms-lg-2"
							onClick={onClose}
						>
							Cancel
						</button>
					</div>
				</div>
			)}
		</BasicModal>
	);
};

export default JobModal;
