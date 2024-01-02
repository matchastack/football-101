// Make an API request to fetch the data from your Flask backend
import { useState, useEffect } from "react";
import "./StandingTable.css";

interface TeamData {
    rank: number;
    team: string;
    points: number;
    goalsDiff: number;
    form: string;
    id: number;
    "all.played": number;
    "all.win": number;
    "all.draw": number;
    "all.lose": number;
    "all.goals.for": number;
    "all.goals.against": number;
    "home.played": number;
    "home.win": number;
    "home.draw": number;
    "home.lose": number;
    "home.goals.for": number;
    "home.goals.against": number;
    "away.played": number;
    "away.win": number;
    "away.draw": number;
    "away.lose": number;
    "away.goals.for": number;
    "away.goals.against": number;
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
            <td>{data["rank"]}</td>
            <td>
                <div className="team-container">
                    <div className="logo-container">
                        <img
                            className="standing-logo"
                            src={`https://media.api-sports.io/football/teams/${data["id"]}.png`}
                            alt="logo"
                        />
                    </div>
                    <span>{data["team"]}</span>
                </div>
            </td>
            <td>{data["all.played"]}</td>
            <td>{data["all.win"]}</td>
            <td>{data["all.draw"]}</td>
            <td>{data["all.lose"]}</td>
            <td>{data["all.goals.for"]}</td>
            <td>{data["all.goals.against"]}</td>
            <td>{data["goalsDiff"]}</td>
            <td>
                <b>{data["points"]}</b>
            </td>
            <td>{formFormat(data["form"])}</td>
            <td>
                <button>
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
    const [data, setData] = useState<TeamData[]>([]); // Specify the type of data as an array of TeamData

    useEffect(() => {
        fetch("http://localhost:9102/premier-league/table")
            .then((response) => response.json())
            .then((data) => setData(JSON.parse(data)))
            .catch((err) => console.error("Error: ", err.message));
    }, []);

    return (
        <table>
            <thead>
                <tr>
                    <th>Position</th>
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
                    <th>More</th>
                </tr>
            </thead>
            <tbody>{data.map((data, index) => entries(data, index))}</tbody>
        </table>
    );
};

export default StandingTable;
