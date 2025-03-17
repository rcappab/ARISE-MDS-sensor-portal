import { createContext } from "react";

export const ObsEditModeContext = createContext({
	obsEditMode: false,
	setObsEditMode: (bool) => {},
});
