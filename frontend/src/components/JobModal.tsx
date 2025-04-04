import React, { useCallback, useContext, useState } from "react";
import { useSearchParams } from "react-router-dom";
import BasicModal from "./BasicModal.tsx";
import { useMutation, useQuery } from "@tanstack/react-query";
import AuthContext from "../context/AuthContext.jsx";
import { getData, postData } from "../utils/FetchFunctions.js";
import toast from "react-hot-toast";
import FormSelect from "./FormSelect.tsx";
import Loading from "./Loading.tsx";

interface Props {
	show?: boolean;
	onClose?: () => void;
}

const JobModal = ({ show = false, onClose = () => {} }: Props) => {
	const [searchParams, setSearchParams] = useSearchParams();
	const { user, authTokens } = useContext(AuthContext);

	const [jobData, setJobData] = useState({
		metadata_type: 0,
		include_files: true,
	});
	const jobName = "create_data_package";

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
		let apiURL = `datafile/queryset_count/?${searchParams.toString()}`;
		let response_json = await getData(apiURL, authTokens.access);
		return response_json;
	};

	const {
		isLoading,
		isError,
		isPending,
		data,
		error,
		isRefetching,
		isPlaceholderData,
		refetch,
	} = useQuery({
		queryKey: ["data", user, "count", searchParams.toString()],
		queryFn: () => getDataFunc(),
	});

	const newPOST = async function (x: { apiURL: string; data: object }) {
		let response_json = await postData(x.apiURL, authTokens.access, x.data);
		//console.log(response_json);
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
			apiURL: `datafile/start_job/${jobName}/?${searchParams.toString()}`,
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

	return (
		<BasicModal
			modalShow={show}
			headerChildren={"Start job"}
		>
			{isLoading ? (
				<Loading />
			) : (
				<div>
					<div>
						Create data package of {data["file_n"]} files of which{" "}
						{data["archived_file_n"]} are archived. Total filesize{" "}
						{data["total_file_size"].toFixed(2)} GB.
					</div>
					<div className="row px-1 py-1 mb-3 border rounded">
						<div className="col-lg-6">
							<FormSelect
								id="metadata_select"
								name="metadata_type"
								value={jobData["metadata_type"]}
								label="metadata type"
								choices={[
									{ label: "Standard", value: 0 },
									{ label: "Camtrap DP", value: 1 },
								]}
								isSearchable={false}
								creatable={false}
								handleChange={(newValue) => {
									setNewDataValue("metadata_type", newValue);
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
									setNewDataValue("include_files", e.target.checked);
								}}
							/>
						</div>
					</div>
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
