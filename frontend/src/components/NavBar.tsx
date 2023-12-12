import { COMPETITIONS, PAGES, makeURL } from "../utils";
import "./NavBar.css";

// Function to map league items (second level)
const mapLeagues = (leagues: string[]) =>
    leagues.map((league) => (
        <li key={league}>
            <a href={makeURL([league])} title={league}>
                {league}
            </a>
            <div className="sublvl-2">
                <ul>{mapPages(league)}</ul>
            </div>
        </li>
    ));

// Function to map page items (third level)
const mapPages = (league: string) =>
    PAGES.map((page) => (
        <li key={page}>
            <a href={makeURL([league, page])} title={page}>
                {page}
            </a>
        </li>
    ));

// Function to map country items (top level)
const mapCountries = () =>
    Object.entries(COMPETITIONS).map(([country, leagues]) => (
        <li key={country}>
            <a href={`#${country}`}>{country}</a>
            <div className="sublvl-1">
                <ul>{mapLeagues(leagues)}</ul>
            </div>
        </li>
    ));

// Create a React component to generate the navigation menu
const NavBar: React.FC = () => {
    return (
        <nav className="nav-bar">
            <ul>{mapCountries()}</ul>
        </nav>
    );
};

export default NavBar;
