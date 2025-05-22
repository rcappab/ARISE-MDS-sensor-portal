import React, { useContext, useRef, useState } from "react";
import { postDataFiles } from "../../utils/FetchFunctions";
import AuthContext from "../../context/AuthContext";
import { useMutation } from "@tanstack/react-query";
import toast from "react-hot-toast";

declare module "react" {
	interface InputHTMLAttributes<T> extends HTMLAttributes<T> {
		webkitdirectory?: string;
	}
}

interface FileStatus {
	[key: string]: { message: string };
}

interface FileStatusDisplayProps {
	fileSuccess: FileStatus[];
	fileSkipped: FileStatus[];
	fileError: FileStatus[];
}

const FileStatusDisplay: React.FC<FileStatusDisplayProps> = ({
	fileSuccess,
	fileSkipped,
	fileError,
}) => {
	const renderFileStatus = (fileStatuses: FileStatus[]) => {
		return fileStatuses.map((fileStatus, index) => (
			<li key={index}>
				{Object.entries(fileStatus)
					.filter(([filename]) => filename !== "status")
					.map(([filename, { message }]) => (
						<div key={filename}>
							<strong>{filename}:</strong> {message}
						</div>
					))}
			</li>
		));
	};

	return (
		<div>
			<div className="d-flex justify-content-evenly">
				<button
					className="btn btn-primary w-100 m-2"
					type="button"
					data-bs-toggle="collapse"
					data-bs-target="#successCollapse"
					aria-expanded="false"
					aria-controls="successCollapse"
					disabled={fileSuccess.length === 0}
				>
					Show Success
				</button>
				<button
					className="btn btn-warning w-100 m-2"
					type="button"
					data-bs-toggle="collapse"
					data-bs-target="#skippedCollapse"
					aria-expanded="false"
					aria-controls="skippedCollapse"
					disabled={fileSkipped.length === 0}
				>
					Show Skipped
				</button>
				<button
					className="btn btn-danger w-100 m-2"
					type="button"
					data-bs-toggle="collapse"
					data-bs-target="#errorCollapse"
					aria-expanded="false"
					aria-controls="errorCollapse"
					disabled={fileError.length === 0}
				>
					Show Failed
				</button>
			</div>
			<div className="mt-3">
				<div
					className="collapse"
					id="successCollapse"
				>
					<h4>Successful uploads</h4>
					<ul>{renderFileStatus(fileSuccess)}</ul>
				</div>
				<div
					className="collapse"
					id="skippedCollapse"
				>
					<h4>Skipped uploads</h4>
					<ul>{renderFileStatus(fileSkipped)}</ul>
				</div>
				<div
					className="collapse"
					id="errorCollapse"
				>
					<h4>Failed uploads</h4>
					<ul>{renderFileStatus(fileError)}</ul>
				</div>
			</div>
		</div>
	);
};

interface UploadFileProps {
	id: string;
	objectType: "deployment" | "device";
}

const UploadFile: React.FC<UploadFileProps> = ({ id, objectType }) => {
	const [isOpen, setIsOpen] = useState(false);
	const [canUpload, setCanUpload] = useState(false);
	const [errorDict, setErrorDict] = useState({});
	const [dirMode, setDirMode] = useState(false);

	const { authTokens } = useContext(AuthContext);

	const filesRef = useRef<HTMLInputElement>(null);

	const updateCanUpload = function () {
		const canUploadBool =
			filesRef.current &&
			filesRef.current.files &&
			filesRef.current.files.length > 0
				? true
				: false;
		setCanUpload(canUploadBool);
	};

	const newPOST = async function (x: {
		apiURL: string;
		newData: object;
		newFiles: File[];
	}) {
		let response_json = await postDataFiles(
			x.apiURL,
			authTokens.access,
			x.newData,
			x.newFiles
		);

		return response_json;
	};

	const doPost = useMutation({
		mutationFn: (inputValue: {
			apiURL: string;
			newData: object;
			newFiles: File[];
		}) => newPOST(inputValue),
	});

	const startLoadingToast = () => {
		const toastId = toast.loading("Loading...");
		return toastId;
	};

	const handleSubmit = async function () {
		if (!canUpload) {
			return;
		}
		const toastId = startLoadingToast();

		setErrorDict({});

		const files: File[] = [];
		if (filesRef.current && filesRef.current.files) {
			for (const file of filesRef.current.files) {
				files.push(file);
			}
		}

		const response = await doPost.mutateAsync({
			apiURL: "datafile/",
			newData: {
				[`${objectType}_ID`]: id,
			},
			newFiles: files,
		});

		if (!response["ok"]) {
			toast.error(
				`Error in submission ${
					response["status_text"] ? ":" + response["status_text"] : ""
				}`,
				{
					id: toastId,
				}
			);
			setErrorDict(response);
		} else {
			toast.success("All files uploaded", {
				id: toastId,
			});
			if (filesRef.current) {
				filesRef.current.value = "";
			}
			setCanUpload(false);
		}
	};

	return (
		<div className="p-2">
			{isOpen ? (
				<>
					<div className="m-1">
						<div className="row">
							<label
								htmlFor="file"
								className="form-label col"
							>
								{!dirMode
									? "Choose files to upload"
									: "Choose directories containing files to upload"}
							</label>
							<div className="form-check form-switch col-lg-4">
								<label htmlFor="dirMode_checkbox">Directory mode</label>
								<input
									name="dir_model"
									className="form-check-input form-control"
									id="dirMode_checkbox"
									type="checkbox"
									checked={dirMode}
									onChange={(e) => {
										setDirMode(e.target.checked);
									}}
								/>
							</div>
						</div>

						<input
							type="file"
							id="file"
							name="file"
							multiple
							ref={filesRef}
							onChange={updateCanUpload}
							className="form-control"
							webkitdirectory={dirMode ? "true" : "false"}
						/>
					</div>
					{Object.keys(errorDict).length > 0 && (
						<FileStatusDisplay
							fileSuccess={errorDict["uploaded_files"]}
							fileError={errorDict["invalid_files"]}
							fileSkipped={errorDict["existing_files"]}
						/>
					)}

					<div className="d-flex justify-content-evenly">
						<button
							className="btn btn-danger m-1 p-2 w-100"
							onClick={() => setIsOpen(false)}
						>
							Cancel
						</button>
						<button
							className="btn btn-primary m-1 p-2 w-100"
							onClick={handleSubmit}
							disabled={!canUpload}
						>
							Submit
						</button>
					</div>
				</>
			) : (
				<button
					className="btn btn-secondary w-100"
					onClick={() => setIsOpen(true)}
				>
					Upload files
				</button>
			)}
		</div>
	);
};

export default UploadFile;
