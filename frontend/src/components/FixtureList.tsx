import { useState, useEffect, useRef, useCallback } from "react";
import "./FixtureList.css";

interface FixtureData {
    id: number;
    date: string;
    venue: string;
    city: string;
    season: number;
    round: string; // to change to number
    "home.id": number;
    "home.name": string;
    "away.id": number;
    "away.name": string;
}

// TODO: Add filter feature

const fixture = (data: FixtureData, index: number) => {
    const t = new Date(data["date"]).toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
    });
    return (
        <li className="match-fixture" key={index}>
            <span className="match-fixture-container">
                <span className="match-fixture-teams">
                    <span className="match-fixture-team">
                        <span className="match-fixture-team-name">
                            {data["home.name"]}
                        </span>
                        <div className="match-fixture-team-logo-container-left">
                            <img
                                className="match-fixture-team-logo"
                                src={`https://media.api-sports.io/football/teams/${data["home.id"]}.png`}
                                alt="logo"
                            />
                        </div>
                    </span>
                    <time>{t}</time>
                    <span className="match-fixture-team">
                        <div className="match-fixture-team-logo-container-right">
                            <img
                                className="match-fixture-team-logo"
                                src={`https://media.api-sports.io/football/teams/${data["away.id"]}.png`}
                                alt="logo"
                            />
                        </div>
                        <span className="match-fixture-team-name">
                            {data["away.name"]}
                        </span>
                    </span>
                </span>
                <span className="match-fixture-location">{data["venue"]}</span>
                <span className="match-fixture-more">...</span>
            </span>
        </li>
    );
};

// TODO: Add infinite scroll feature
const FixtureList = () => {
    const [data, setData] = useState<FixtureData[]>([]);
    const [page, setPage] = useState(1);

    const fetchData = (page: number) => {
        fetch(`http://localhost:9102/premier-league/fixtures?page=${page}`)
            .then((res) => res.json())
            .then((newData) =>
                setData((prevData) => [...prevData, ...JSON.parse(newData)])
            )
            .catch((err) => console.log("Error: ", err.message));
    };

    useEffect(() => {
        fetchData(page);
    }, [page]);

    const observer = useRef<IntersectionObserver | null>(null);
    const lastFixtureElementRef = useCallback(
        (node: HTMLElement | null) => {
            if (observer.current) observer.current.disconnect();
            observer.current = new IntersectionObserver((entries) => {
                if (entries[0].isIntersecting) {
                    setPage((prevPage) => prevPage + 1);
                }
            });
            if (node) observer.current.observe(node);
        },
        [] // Depend on your data fetching state variables
    );

    return (
        <>
            <ul className="match-list">
                {data.map((match, index) => {
                    if (data.length === index + 1) {
                        return (
                            <li ref={lastFixtureElementRef}>
                                {fixture(match, index)}
                            </li>
                        );
                    } else {
                        return <li>{fixture(match, index)}</li>;
                    }
                })}
            </ul>
        </>
    );
};
export default FixtureList;
