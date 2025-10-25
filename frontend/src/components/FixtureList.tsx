import { useState, useEffect } from "react";
import "./FixtureList.css";

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
        <li className="match-fixture" key={index}>
            <span className="match-fixture-container">
                <span className="match-fixture-teams">
                    <span className="match-fixture-team">
                        <span className="match-fixture-team-name">
                            {data.home_name}
                        </span>
                        <div className="match-fixture-team-logo-container-left">
                            <img
                                className="match-fixture-team-logo"
                                src={`https://media.api-sports.io/football/teams/${data.home_id}.png`}
                                alt="logo"
                            />
                        </div>
                    </span>
                    <time>{scoreOrTime}</time>
                    <span className="match-fixture-team">
                        <div className="match-fixture-team-logo-container-right">
                            <img
                                className="match-fixture-team-logo"
                                src={`https://media.api-sports.io/football/teams/${data.away_id}.png`}
                                alt="logo"
                            />
                        </div>
                        <span className="match-fixture-team-name">
                            {data.away_name}
                        </span>
                    </span>
                </span>
                <span className="match-fixture-location">{data.venue}</span>
                <span className="match-fixture-more">...</span>
            </span>
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
        fetch("http://localhost:9102/api/seasons?league=Premier%20League")
            .then((response) => response.json())
            .then((result) => {
                if (result.success) {
                    setSeasons(result.data);
                    // Set current season as default
                    const currentSeason = result.data.find((s: Season) => s.is_current);
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

        fetch(`http://localhost:9102/api/fixtures?league=Premier%20League&season=${selectedSeason}`)
            .then((response) => response.json())
            .then((result) => {
                if (result.success) {
                    setData(result.data);
                } else {
                    setError(result.error || "Failed to fetch fixtures");
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
        <div>
            <div className="season-selector">
                <label htmlFor="season-select">Season: </label>
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

            {loading ? (
                <div className="loading">Loading fixtures...</div>
            ) : error ? (
                <div className="error">{error}</div>
            ) : (
                <ul className="match-list">
                    {data.map((match, index) => fixture(match, index))}
                </ul>
            )}
        </div>
    );
};
export default FixtureList;
