import React, { useState } from "react";
import FormSelectTZ from "./FormSelectTZ.tsx";
import FormDateSelector from "./FormDateSelector.tsx";
import { fullDateTimeString } from "../utils/timezoneFunctions.js";
import { fromZonedTime } from "date-fns-tz";

interface Props {
	id: string;
	name: string;
	label: string;
	text: string;
}

const FormDateTZSelect = ({ id, name, label, text }: Props) => {
	const [timeZone, setTimeZone] = useState(String);
	const [dateTime, setDateTime] = useState(String);
	const [dateTimeString, setDateTimeString] = useState(String);

	const setTimeZoneFromField = function (newValue) {
		console.log(newValue);
		setTimeZone(newValue);

		setDateTimeString(fromZonedTime(dateTime, newValue).toJSON());
	};

	const setDateTimeFromField = function (e) {
		console.log(e.target.value);

		let newValue = e.target.value;

		setDateTime(newValue);

		setDateTimeString(fromZonedTime(newValue, timeZone).toJSON());
	};

	return (
		<div className="form-floating">
			<input
				id={id}
				name={name}
				defaultValue={dateTimeString}
				value={dateTimeString}
				className="d-none"
			/>
			<div className="row">
				<FormDateSelector
					id={`${id}_dt`}
					name={`${name}_dt`}
					label={label}
					handleChange={setDateTimeFromField}
					className="col"
				/>

				<FormSelectTZ
					id={`${id}_TZ`}
					name={`${name}_TZ`}
					label="Timezone"
					handleChange={setTimeZoneFromField}
					className="col"
				/>
			</div>

			<div className="form-text">
				{text}
				<div className="invalid-feedback"></div>
			</div>
		</div>
	);
};

export default FormDateTZSelect;
