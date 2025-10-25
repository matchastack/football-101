import { COMPETITIONS, PAGES, makeURL } from "../utils";

// Function to map league items (second level)
const mapLeagues = (leagues: string[]) =>
    leagues.map((league) => (
        <li key={league} className="relative group/league">
            <a
                href={makeURL([league])}
                title={league}
                className="block px-4 py-3 text-gray-700 hover:bg-gray-100 hover:text-primary transition-all duration-150 rounded-md hover:translate-x-1"
            >
                {league}
            </a>
            <div className="hidden group-hover/league:block absolute left-full top-0 min-w-[200px] bg-white rounded-lg shadow-card-lg p-2 ml-2 z-50 animate-fadeIn">
                <ul className="list-none p-0 m-0">{mapPages(league)}</ul>
            </div>
        </li>
    ));

// Function to map page items (third level)
const mapPages = (league: string) =>
    PAGES.map((page) => (
        <li key={page}>
            <a
                href={makeURL([league, page])}
                title={page}
                className="block px-4 py-3 text-gray-700 hover:bg-gray-100 hover:text-primary transition-all duration-150 rounded-md hover:translate-x-1 whitespace-nowrap"
            >
                {page}
            </a>
        </li>
    ));

// Function to map country items (top level)
const mapCountries = () =>
    Object.entries(COMPETITIONS).map(([country, leagues]) => (
        <li key={country} className="relative group">
            <a
                href={`#${country}`}
                className="block px-5 py-3.5 text-white font-medium text-[0.9375rem] rounded-md hover:bg-white/10 transition-all duration-200 hover:-translate-y-0.5"
            >
                {country}
            </a>
            <div className="hidden group-hover:block absolute top-full left-0 min-w-[200px] bg-white rounded-lg shadow-card-lg p-2 mt-2 z-50 animate-fadeIn">
                <ul className="list-none p-0 m-0">{mapLeagues(leagues)}</ul>
            </div>
        </li>
    ));

// Create a React component to generate the navigation menu
const NavBar: React.FC = () => {
    return (
        <nav className="bg-black/15 backdrop-blur-md">
            <ul className="list-none flex gap-1 px-8 m-0">{mapCountries()}</ul>
        </nav>
    );
};

export default NavBar;
