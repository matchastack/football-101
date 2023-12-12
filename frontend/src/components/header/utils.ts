export const COMPETITIONS = {
    England: ["Premier League"],
    Germany: ["Bundesliga"],
    Spain: ["La Liga"],
    Italy: ["Serie A"],
};

export const PAGES = ["Teams", "Fixtures", "Results", "Analytics"];

export const hypenName = (name: string) => {
    return name.toLowerCase().replace(" ", "-");
};

export const makeURL = (names: string[]) => {
    return "/" + names.map((name) => hypenName(name)).join("/");
};