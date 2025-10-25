import { useState, useEffect } from "react";
import axios from "axios";
import "./StandingTable.css";

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
    return (
        <div className="form">
            {formArray.map((result, index) => (
                <span key={index} className={`result ${result}`}>
                    {result}
                </span>
            ))}
        </div>
    );
};

const entries = (data: TeamData, index: number) => {
    return (
        <tr className="table-entry" key={index}>
            <td>{data.rank}</td>
            <td>
                <div className="team-container">
                    <div className="logo-container">
                        <img
                            className="standing-logo"
                            src={`https://media.api-sports.io/football/teams/${data.id}.png`}
                            alt="logo"
                        />
                    </div>
                    <span>{data.team}</span>
                </div>
            </td>
            <td>{data.played}</td>
            <td>{data.wins}</td>
            <td>{data.draws}</td>
            <td>{data.losses}</td>
            <td>{data.goals_for}</td>
            <td>{data.goals_against}</td>
            <td>{data.goal_difference}</td>
            <td>
                <b>{data.points}</b>
            </td>
            <td>{formFormat(data.form)}</td>
            <td>
                <button className="expand-more">
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
        <div className="standings-container">
            <div className="standings-header">
                <h1 className="standings-title">Premier League Standings</h1>
                <div className="season-selector">
                    <label htmlFor="season-select">Season:</label>
                    <select
                        id="season-select"
                        value={selectedSeason}
                        onChange={(e) => setSelectedSeason(Number(e.target.value))}
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
                <div className="loading">Loading standings...</div>
            ) : error ? (
                <div className="error">{error}</div>
            ) : (
                <table>
                    <thead>
                        <tr>
                            <th>Pos</th>
                            <th>Club</th>
                            <th>Played</th>
                            <th>Won</th>
                            <th>Drawn</th>
                            <th>Lost</th>
                            <th>GF</th>
                            <th>GA</th>
                            <th>GD</th>
                            <th>Points</th>
                            <th>Form</th>
                            <th></th>
                        </tr>
                    </thead>
                    <tbody>{data.map((teamData, index) => entries(teamData, index))}</tbody>
                </table>
            )}
        </div>
    );
};

export default StandingTable;
