import { useState, useEffect } from "react";
import axios from "axios";

interface TeamData {
    rank: number;
    id: number;
    team: string;
    logo_url: string | null;
    points: number;
    played: number;
    wins: number;
    draws: number;
    losses: number;
    goals_for: number;
    goals_against: number;
    goal_difference: number;
    form: string;
    home_played: number;
    home_wins: number;
    home_draws: number;
    home_losses: number;
    home_goals_for: number;
    home_goals_against: number;
    away_played: number;
    away_wins: number;
    away_draws: number;
    away_losses: number;
    away_goals_for: number;
    away_goals_against: number;
}

interface Season {
    id: number;
    year: number;
    is_current: boolean;
}

const formFormat = (form: string) => {
    const formArray = form.split("");
    const getResultClass = (result: string) => {
        if (result === 'W') return 'bg-gradient-to-br from-green-500 to-green-600';
        if (result === 'D') return 'bg-gradient-to-br from-gray-500 to-gray-600';
        if (result === 'L') return 'bg-gradient-to-br from-red-500 to-red-600';
        return '';
    };

    return (
        <div className="flex gap-1 flex-nowrap justify-start">
            {formArray.map((result, index) => (
                <span
                    key={index}
                    className={`flex justify-center items-center w-7 h-7 rounded-md text-white font-bold text-xs transition-transform hover:scale-110 ${getResultClass(result)}`}
                >
                    {result}
                </span>
            ))}
        </div>
    );
};

const entries = (data: TeamData, index: number) => {
    // Determine border color based on position
    let borderColor = '';
    if (index < 4) borderColor = 'border-l-4 border-l-secondary'; // Champions League
    else if (index === 4) borderColor = 'border-l-4 border-l-amber-400'; // Europa League
    else if (index >= 17) borderColor = 'border-l-4 border-l-accent'; // Relegation

    return (
        <tr
            key={index}
            className={`transition-all duration-200 border-b border-gray-100 hover:bg-gray-50 hover:scale-[1.002] ${borderColor}`}
        >
            <td className="px-6 py-[1.125rem] pl-6 font-bold text-gray-900 text-base">{data.rank}</td>
            <td className="px-3.5 py-[1.125rem] text-[0.9375rem] text-gray-700">
                <div className="flex items-center gap-3 min-w-[200px]">
                    <div className="flex-shrink-0 w-8 h-8 flex items-center justify-center">
                        <img
                            className="w-full h-full object-contain"
                            src={`https://media.api-sports.io/football/teams/${data.id}.png`}
                            alt="logo"
                        />
                    </div>
                    <span className="font-semibold text-gray-900">{data.team}</span>
                </div>
            </td>
            <td className="px-3.5 py-[1.125rem] text-[0.9375rem] text-gray-700">{data.played}</td>
            <td className="px-3.5 py-[1.125rem] text-[0.9375rem] text-gray-700">{data.wins}</td>
            <td className="px-3.5 py-[1.125rem] text-[0.9375rem] text-gray-700">{data.draws}</td>
            <td className="px-3.5 py-[1.125rem] text-[0.9375rem] text-gray-700">{data.losses}</td>
            <td className="px-3.5 py-[1.125rem] text-[0.9375rem] text-gray-700">{data.goals_for}</td>
            <td className="px-3.5 py-[1.125rem] text-[0.9375rem] text-gray-700">{data.goals_against}</td>
            <td className="px-3.5 py-[1.125rem] text-[0.9375rem] text-gray-700">{data.goal_difference}</td>
            <td className="px-3.5 py-[1.125rem] text-[0.9375rem] text-gray-700">
                <b className="text-lg text-primary">{data.points}</b>
            </td>
            <td className="px-3.5 py-[1.125rem] text-[0.9375rem] text-gray-700">{formFormat(data.form)}</td>
            <td className="px-6 pr-6 py-[1.125rem] text-[0.9375rem] text-gray-700">
                <button className="border-none bg-transparent cursor-pointer p-1.5 rounded-md transition-all duration-200 text-gray-400 hover:bg-gray-100 hover:text-primary hover:rotate-180">
                    <svg
                        width="24"
                        height="24"
                        viewBox="0 0 24 24"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                    >
                        <path
                            d="M6.34317 7.75732L4.92896 9.17154L12 16.2426L19.0711 9.17157L17.6569 7.75735L12 13.4142L6.34317 7.75732Z"
                            fill="currentColor"
                        />
                    </svg>
                </button>
            </td>
        </tr>
    );
};

const StandingTable = () => {
    const [data, setData] = useState<TeamData[]>([]);
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

    // Fetch standings for selected season
    useEffect(() => {
        setLoading(true);
        setError(null);

        axios.get("http://localhost:9102/api/standings", {
            params: {
                league: "Premier League",
                season: selectedSeason
            }
        })
            .then((response) => {
                if (response.data.success) {
                    setData(response.data.data);
                } else {
                    setError(response.data.error || "Failed to fetch standings");
                }
                setLoading(false);
            })
            .catch((err) => {
                console.error("Error: ", err.message);
                setError("Failed to fetch standings");
                setLoading(false);
            });
    }, [selectedSeason]);

    return (
        <div className="max-w-[1400px] mx-auto my-8 px-6">
            <div className="bg-white p-6 md:p-8 rounded-xl shadow-card mb-6">
                <h1 className="text-3xl font-bold text-gray-900 mb-4">Premier League Standings</h1>
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
                    <p className="text-gray-600 text-lg">Loading standings...</p>
                </div>
            ) : error ? (
                <div className="text-center py-12 bg-white rounded-xl shadow-card">
                    <p className="text-accent text-lg font-medium">{error}</p>
                </div>
            ) : (
                <div className="overflow-hidden rounded-xl shadow-card">
                    <table className="w-full border-separate border-spacing-0 bg-white">
                        <thead className="bg-gradient-to-br from-primary to-primary-light">
                            <tr>
                                <th className="px-6 py-4 pl-6 text-left font-semibold text-sm uppercase tracking-wider text-white whitespace-nowrap">
                                    Pos
                                </th>
                                <th className="px-3.5 py-4 text-left font-semibold text-sm uppercase tracking-wider text-white whitespace-nowrap">
                                    Club
                                </th>
                                <th className="px-3.5 py-4 text-left font-semibold text-sm uppercase tracking-wider text-white whitespace-nowrap">
                                    Played
                                </th>
                                <th className="px-3.5 py-4 text-left font-semibold text-sm uppercase tracking-wider text-white whitespace-nowrap">
                                    Won
                                </th>
                                <th className="px-3.5 py-4 text-left font-semibold text-sm uppercase tracking-wider text-white whitespace-nowrap">
                                    Drawn
                                </th>
                                <th className="px-3.5 py-4 text-left font-semibold text-sm uppercase tracking-wider text-white whitespace-nowrap">
                                    Lost
                                </th>
                                <th className="px-3.5 py-4 text-left font-semibold text-sm uppercase tracking-wider text-white whitespace-nowrap">
                                    GF
                                </th>
                                <th className="px-3.5 py-4 text-left font-semibold text-sm uppercase tracking-wider text-white whitespace-nowrap">
                                    GA
                                </th>
                                <th className="px-3.5 py-4 text-left font-semibold text-sm uppercase tracking-wider text-white whitespace-nowrap">
                                    GD
                                </th>
                                <th className="px-3.5 py-4 text-left font-semibold text-sm uppercase tracking-wider text-white whitespace-nowrap">
                                    Points
                                </th>
                                <th className="px-3.5 py-4 text-left font-semibold text-sm uppercase tracking-wider text-white whitespace-nowrap">
                                    Form
                                </th>
                                <th className="px-6 pr-6 py-4 text-left font-semibold text-sm uppercase tracking-wider text-white whitespace-nowrap"></th>
                            </tr>
                        </thead>
                        <tbody>{data.map((teamData, index) => entries(teamData, index))}</tbody>
                    </table>
                </div>
            )}
        </div>
    );
};

export default StandingTable;
