import React from "react";
import { Outlet, useOutletContext, useParams } from "react-router-dom";
import {
	getNameKey,
	getValidGalleries,
	getValidParents,
	getValidObject,
	getFilterKey,
} from "../utils/objectChecks";
import Error404page from "../pages/Error404page";

type objectContextType = {
	fromObject: string | undefined;
	fromID: string | undefined;
	objectType: string | undefined;
	nameKey: string;
	validGalleries: string[];
	validParents: string[];
	filterKey: string;
};

export const ObjectTypeCheck = () => {
	let { fromObject, fromID, objectType } = useParams();

	if (objectType === undefined) {
		objectType = fromObject;
		fromObject = undefined;
	} else if (fromObject !== undefined) {
		fromObject = fromObject.substring(0, fromObject.length - 1);
	}
	if (objectType !== undefined) {
		objectType = objectType.substring(0, objectType.length - 1);
	}

	let error = false;

	const isValidObject = getValidObject(objectType);
	if (!isValidObject) {
		error = true;
	}

	const nameKey = getNameKey(objectType) as string;
	if (fromID !== undefined && fromObject !== undefined) {
		const validFromGalleries = getValidGalleries(fromObject);

		if (
			validFromGalleries === undefined ||
			!validFromGalleries.includes(objectType)
		) {
			error = true;
		}
	}

	const validGalleries = getValidGalleries(objectType) as string[];
	const validParents = getValidParents(objectType) as string[];
	const filterKey = getFilterKey(fromObject) as string;

	const contextData = {
		fromObject: fromObject,
		fromID: fromID,
		objectType: objectType,
		nameKey: nameKey,
		validGalleries: validGalleries,
		validParents: validParents,
		filterKey: filterKey,
	} as objectContextType;

	if (error) {
		return <Error404page />;
	}

	return <Outlet context={contextData} />;
};

export function useObjectType() {
	return useOutletContext<objectContextType>();
}
