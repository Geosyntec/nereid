import { Tabs } from "./tabs.js";
import { editTab } from "./editor-tab";
import {
  treatmentFacilityResultsTab,
  landSurfaceResultsTab,
} from "./results-tab";
import { HowTab } from "./howto-tab.js";

const howTab = new HowTab({ id: "how-to-tab" });

export const tabs = new Tabs({
  children: [
    editTab,
    treatmentFacilityResultsTab,
    landSurfaceResultsTab,
    howTab,
  ],
});
