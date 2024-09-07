import React from "react";
import { useState, useEffect, useContext } from "react";
import { getData } from "../utils/FetchFunctions";
import AuthContext from "../context/AuthContext";
import GalleryForm from "./GalleryForm";
import GalleryDisplay from "./GalleryDisplay.tsx";
import GalleryPageControls from "./GalleryPageControls.tsx";
import Modal from "./Modal.tsx";
import DetailModalHeader from "./DetailModalHeader.jsx";
import DetailDisplay from "./DetailDisplay.tsx";
import DetailEdit from "./DetailEdit.tsx";
import Loading from "./Loading.tsx";
import { useQuery, keepPreviousData } from "@tanstack/react-query";
import { useSearchParams, useNavigate } from "react-router-dom";

const Gallery = () => {
	const [searchParams, setSearchParams] = useSearchParams();
	const [formKeys, setFormKeys] = useState();
	const [pageNum, setPageNum] = useState(searchParams.get("page") || 1);
	const { authTokens } = useContext(AuthContext);
	const navigate = useNavigate();

	const checkSearchParameters = function () {
		let searchParamsObject = Object.fromEntries(searchParams);
		if (formKeys) {
			Object.entries(searchParamsObject).forEach(([key, value]) => {
				if (!formKeys.includes(key)) {
					delete searchParamsObject[key];
				}
			});
		}
		return new URLSearchParams(searchParamsObject);
	};

	const updateSearchParameters = function (key, val) {
		let oldSearchParams = searchParams;
		if (oldSearchParams.size > 0) {
			oldSearchParams.set(key, val);
			setSearchParams(oldSearchParams);
		}
	};

	const removeSearchParameters = function (key) {
		let oldSearchParams = searchParams;
		oldSearchParams.delete(key);
		setSearchParams(oldSearchParams);
	};

	useEffect(() => {
		console.log(pageNum);
		updateSearchParameters("page", pageNum);
	}, [pageNum]);

	const getDataFunc = async (currentSearchParams) => {
		let apiURL = `deployment/?${currentSearchParams.toString()}`;
		console.log(apiURL);
		let response_json = await getData(apiURL, authTokens.access);
		return response_json;
	};

	const { isLoading, isError, isPending, data, error, isPlaceholderData } =
		useQuery({
			queryKey: ["data", "username", checkSearchParameters().toString()],
			queryFn: () => getDataFunc(searchParams),
			enabled: searchParams.size > 0,
			placeholderData: keepPreviousData,
		});

	const onSubmit = function () {
		setPageNum(1);
	};

	const changePage = function (newPage) {
		console.log(newPage);
		setPageNum(newPage);
	};

	const openDetail = function (index) {
		updateSearchParameters("detail", index);
	};

	const closeDetail = function () {
		console.log("close detail");
		removeSearchParameters("detail");
	};

	const setEdit = function (editOn = true) {
		if (editOn) {
			updateSearchParameters("edit", editOn);
		} else {
			removeSearchParameters("edit");
		}
	};

	const showGallery = function () {
		if (isLoading || isPending) {
			return <Loading />;
		}

		if (isError) {
			return <p>An error occurred: {error.message}</p>;
		}

		let maxPage = Math.ceil(data.count / searchParams.get("page_size"));

		return (
			<div>
				<GalleryPageControls
					pageNum={pageNum}
					changePageCallback={changePage}
					maxPage={maxPage}
				/>
				<div
					id="display-container"
					className={isPlaceholderData ? "opacity-50" : ""}
				>
					<GalleryDisplay
						data={data.results}
						onTileClick={openDetail}
					/>
				</div>
			</div>
		);
	};

	const showDetailModal = function () {
		//console.log(searchParams.get("detail") && data !== undefined);
		let modalShow = searchParams.get("detail") && data;
		if (!modalShow) {
			return null;
		}
		let detailNum = searchParams.get("detail");
		let selectedData = data.results[detailNum];
		let maxPage = Math.ceil(data.count / searchParams.get("page_size"));
		let maxData = data.results.length;
		let editMode = searchParams.get("edit");

		console.log(selectedData);
		return (
			<Modal
				modalShow={modalShow}
				onClose={closeDetail}
				headerChildren={
					<DetailModalHeader
						detailNum={detailNum}
						pageNum={pageNum}
						maxPage={maxPage}
						maxDetail={maxData}
						handleDetailChange={openDetail}
						handlePageChange={changePage}
						isLoading={isLoading | isPlaceholderData}
						editMode={editMode}
						handleEdit={setEdit}
					>
						{selectedData["deployment_deviceID"]}
					</DetailModalHeader>
				}
			>
				{editMode ? (
					<DetailEdit selectedData={selectedData} />
				) : (
					<DetailDisplay selectedData={selectedData} />
				)}
			</Modal>
		);
	};

	return (
		<div className="container-lg">
			<div>
				{showDetailModal()}
				<GalleryForm
					onSubmit={onSubmit}
					setFormKeys={setFormKeys}
				/>
				{showGallery()}
			</div>
		</div>
	);
};

export default Gallery;
