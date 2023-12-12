import "./Header.css";
import NavBar from "./NavBar";

const TopHeader = () => {
    return (
        <div className="logo">
            <a href="/home">
                <img
                    width="300"
                    height="80"
                    src="./src/assets/images/White logo - no background.svg"
                    alt="Football 101 Logo"
                />
            </a>
        </div>
    );
};

const Header = () => {
    return (
        <header className="header-top">
            <TopHeader />
            <NavBar />
        </header>
    );
};

export default Header;
