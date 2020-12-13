import dayjs from "dayjs";
import utc from "dayjs/plugin/utc";
import timezone from "dayjs/plugin/timezone";

dayjs.extend(utc);
dayjs.extend(timezone);

// eslint-disable-next-line import/prefer-default-export
export function getIsoDate(validAt: string | dayjs.Dayjs) {
    const date: dayjs.Dayjs = typeof validAt === "string" ? dayjs(validAt) : validAt;
    return date.tz(dayjs.tz.guess()).utc().toISOString();
}
