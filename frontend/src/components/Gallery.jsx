import React from "react";
import { useState, useEffect, useContext } from "react";
import getData from "../utils/FetchFunctions";
import AuthContext from "../context/AuthContext";
import GalleryForm from "./GalleryForm";
import GalleryDisplay from "./GalleryDisplay.tsx";
import GalleryPageControls from "./GalleryPageControls.tsx";
import Loading from "./Loading.jsx";
import { useQuery, keepPreviousData } from "@tanstack/react-query";
import { useSearchParams } from "react-router-dom";

const Gallery = () => {
	const [searchParams, setSearchParams] = useSearchParams();
	const [pageNum, setPageNum] = useState(searchParams.get("page") || 1);
	const { authTokens } = useContext(AuthContext);

	const getDataFunc = async (searchParams) => {
		let apiURL = `deployment/?${searchParams.toString()}`;
		console.log(apiURL);
		let response = await getData(apiURL, authTokens.access);
		return response.json();
	};

	const { isLoading, isError, isPending, data, error, isPreviousData } =
		useQuery({
			queryKey: ["data", "username", searchParams.toString()],
			queryFn: () => getDataFunc(searchParams),
			enabled: searchParams.size > 0,
			placeholderData: keepPreviousData,
		});

	const onSubmit = function () {
		setPageNum(1);
	};

	useEffect(() => {
		console.log(pageNum);
		let oldSearchParams = searchParams;
		if (oldSearchParams.size > 0) {
			oldSearchParams.set("page", pageNum);
			console.log(oldSearchParams);
			setSearchParams(oldSearchParams);
		}
	}, [pageNum]);

	const changePage = function (newPage) {
		console.log(newPage);
		setPageNum(newPage);
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
					className={isPreviousData ? "opacity-50" : ""}
				>
					<GalleryDisplay data={data.results} />
				</div>
			</div>
		);
	};

	return (
		<div className="container-lg">
			<div>
				<GalleryForm onSubmit={onSubmit} />
				{showGallery()}
			</div>
		</div>
	);
};

export default Gallery;
