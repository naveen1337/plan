import { HomeUi } from "./home_ui";
import { HOME_METRICS } from "./home_ctrl";

export function HomeScreen() {
  return <HomeUi metrics={HOME_METRICS} />;
}
