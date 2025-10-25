import { useState, useEffect } from "react";
import axios from "axios";

interface FixtureData {
    id: number;
    date: string;
    round: string;
    venue: string;
    city: string;
    home_id: number;
    home_name: string;
    away_id: number;
    away_name: string;
    home_score: number | null;
    away_score: number | null;
    status: string;
}

interface Season {
    id: number;
    year: number;
    is_current: boolean;
}

// TODO: Add filter feature

const fixture = (data: FixtureData, index: number) => {
    const t = new Date(data.date).toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
    });

    // Show score if match has been played, otherwise show time
    const scoreOrTime = data.home_score !== null && data.away_score !== null
        ? `${data.home_score} - ${data.away_score}`
        : t;

    return (
        <li key={index} className="bg-white rounded-xl shadow-card transition-all duration-300 overflow-hidden border border-gray-100 hover:shadow-card-lg hover:-translate-y-0.5 hover:border-primary">
            <div className="grid grid-cols-[1fr_auto_1fr] md:grid-cols-[1fr_auto_1fr_auto] gap-4 md:gap-6 items-center p-4 md:p-6">
                {/* Home Team */}
                <div className="flex items-center gap-3 justify-end text-right">
                    <span className="font-semibold text-[1.0625rem] text-gray-900 whitespace-nowrap overflow-hidden text-ellipsis">
                        {data.home_name}
                    </span>
                    <div className="flex-shrink-0 w-10 h-10 md:w-10 md:h-10 flex items-center justify-center bg-gray-50 rounded-lg p-1.5">
                        <img
                            className="w-full h-full object-contain"
                            src={`https://media.api-sports.io/football/teams/${data.home_id}.png`}
                            alt={`${data.home_name} logo`}
                        />
                    </div>
                </div>

                {/* Time/Score */}
                <time className="flex flex-col items-center justify-center px-4 md:px-6 py-3 bg-gradient-to-br from-primary to-primary-light text-white font-bold text-lg rounded-lg min-w-[80px] text-center">
                    {scoreOrTime}
                </time>

                {/* Away Team */}
                <div className="flex items-center gap-3 justify-start text-left">
                    <div className="flex-shrink-0 w-10 h-10 md:w-10 md:h-10 flex items-center justify-center bg-gray-50 rounded-lg p-1.5">
                        <img
                            className="w-full h-full object-contain"
                            src={`https://media.api-sports.io/football/teams/${data.away_id}.png`}
                            alt={`${data.away_name} logo`}
                        />
                    </div>
                    <span className="font-semibold text-[1.0625rem] text-gray-900 whitespace-nowrap overflow-hidden text-ellipsis">
                        {data.away_name}
                    </span>
                </div>

                {/* Venue - spans all columns on mobile */}
                <div className="col-span-3 md:col-span-1 pt-4 md:pt-0 md:pl-4 border-t md:border-t-0 md:border-l border-gray-100 flex items-center gap-2 text-gray-600 text-[0.9375rem]">
                    <span className="text-base">📍</span>
                    {data.venue}
                </div>
            </div>
        </li>
    );
};

const FixtureList = () => {
    const [data, setData] = useState<FixtureData[]>([]);
    const [seasons, setSeasons] = useState<Season[]>([]);
    const [selectedSeason, setSelectedSeason] = useState<number>(2024);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    // Fetch available seasons
    useEffect(() => {
        axios.get("http://localhost:9102/api/seasons", {
            params: { league: "Premier League" }
        })
            .then((response) => {
                if (response.data.success) {
                    setSeasons(response.data.data);
                    // Set current season as default
                    const currentSeason = response.data.data.find((s: Season) => s.is_current);
                    if (currentSeason) {
                        setSelectedSeason(currentSeason.year);
                    }
                }
            })
            .catch((err) => console.error("Error fetching seasons: ", err.message));
    }, []);

    // Fetch fixtures for selected season
    useEffect(() => {
        setLoading(true);
        setError(null);

        axios.get("http://localhost:9102/api/fixtures", {
            params: {
                league: "Premier League",
                season: selectedSeason
            }
        })
            .then((response) => {
                if (response.data.success) {
                    setData(response.data.data);
                } else {
                    setError(response.data.error || "Failed to fetch fixtures");
                }
                setLoading(false);
            })
            .catch((err) => {
                console.error("Error: ", err.message);
                setError("Failed to fetch fixtures");
                setLoading(false);
            });
    }, [selectedSeason]);

    return (
        <div className="max-w-[1200px] mx-auto my-8 px-6">
            <div className="bg-white p-6 md:p-8 rounded-xl shadow-card mb-6">
                <h1 className="text-3xl font-bold text-gray-900 mb-4">Premier League Fixtures</h1>
                <div className="flex items-center gap-3">
                    <label htmlFor="season-select" className="font-semibold text-gray-700 text-[0.9375rem]">
                        Season:
                    </label>
                    <select
                        id="season-select"
                        value={selectedSeason}
                        onChange={(e) => setSelectedSeason(Number(e.target.value))}
                        className="px-4 py-2.5 border-2 border-gray-200 rounded-lg text-[0.9375rem] font-medium text-gray-900 bg-white cursor-pointer transition-all duration-200 hover:border-primary focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/10"
                    >
                        {seasons.map((season) => (
                            <option key={season.id} value={season.year}>
                                {season.year}/{season.year + 1}
                                {season.is_current ? " (Current)" : ""}
                            </option>
                        ))}
                    </select>
                </div>
            </div>

            {loading ? (
                <div className="text-center py-12 bg-white rounded-xl shadow-card">
                    <p className="text-gray-600 text-lg">Loading fixtures...</p>
                </div>
            ) : error ? (
                <div className="text-center py-12 bg-white rounded-xl shadow-card">
                    <p className="text-accent text-lg font-medium">{error}</p>
                </div>
            ) : (
                <ul className="list-none p-0 m-0 grid gap-4">
                    {data.map((match, index) => fixture(match, index))}
                </ul>
            )}
        </div>
    );
};
export default FixtureList;
