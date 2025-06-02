import React, { useContext, useState } from "react";
import FormSelect from "./FormSelect.tsx";
import { useQuery, useMutation } from "@tanstack/react-query";
import AuthContext from "../../context/AuthContext.jsx";
import { getData, postData } from "../../utils/FetchFunctions.js";

interface Props {
	name: string;
	id: string;
	value?: string | string[] | null;
	label: string;
	choices: [];
	apiSearchKey?: string | null;
	isSearchable?: boolean;
	isClearable?: boolean;
	apiURL: string;
	valueKey?: string;
	labelKey?: string;
	multiple?: boolean;
	creatable?: boolean;
	refetchOnInput?: boolean;
	handleChange?: (e) => void;
	valid?: boolean;
}

const FormSelectAPI = ({
	name,
	id,
	apiURL,
	value = null,
	label,
	choices = [],
	apiSearchKey = null,
	isSearchable = true,
	isClearable = true,
	valueKey = undefined,
	labelKey = undefined,
	multiple = false,
	creatable = false,
	refetchOnInput = true,
	handleChange = () => {},
	valid = true,
}: Props) => {
	const { user, authTokens } = useContext(AuthContext);
	const [searchString, setSearchString] = useState(value);
	const getDataFunc = async () => {
		if (apiURL === "") {
			return [];
		}
		let fullAPIURL;

		if (apiSearchKey !== null && searchString !== null) {
			fullAPIURL = `${apiURL}?${apiSearchKey}=${searchString}`;
		} else {
			fullAPIURL = apiURL;
		}
		let response_json = await getData(fullAPIURL, authTokens.access);

		if ("results" in response_json) {
			response_json = response_json["results"];
		}

		let newOptions = response_json.map((x) => {
			if (valueKey !== undefined && labelKey !== undefined) {
				return { value: String(x[valueKey]), label: x[labelKey] };
			} else {
				return { value: String(x), label: x };
			}
		});
		let allOptions = choices.concat(newOptions);
		return allOptions;
	};

	const { data, isLoading, refetch } = useQuery({
		queryKey: [user, apiURL],
		queryFn: getDataFunc,
		refetchOnWindowFocus: false,
	});

	const handleCreate = async (newvalue: string) => {
		let results = await doCreate.mutateAsync(newvalue);
		if (labelKey && valueKey) {
			return { label: results[labelKey], value: results[valueKey] };
		} else {
			return { value: results["value"], label: results["label"] };
		}
	};

	const doCreate = useMutation({
		mutationFn: (inputValue: any) => newPOST(inputValue),
	});

	const onInput = function (newValue) {
		setSearchString(newValue);
		if (apiSearchKey && refetchOnInput) {
			refetch();
		}
	};

	const newPOST = async (inputValue) => {
		let newData = {};
		if (labelKey) {
			newData[labelKey] = inputValue;
		} else {
			newData["label"] = inputValue;
		}

		let response_json = await postData(apiURL, authTokens.access, newData);
		refetch();
		return response_json;
	};

	return (
		<FormSelect
			key={id}
			name={name}
			id={id}
			value={isLoading ? null : value}
			label={label}
			choices={data}
			isLoading={isLoading}
			isSearchable={isSearchable}
			multiple={multiple}
			creatable={creatable}
			handleCreate={handleCreate}
			handleChange={handleChange}
			handleInput={onInput}
			isClearable={isClearable}
			valid={valid}
		/>
	);
};

export default FormSelectAPI;
