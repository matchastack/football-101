import "./Header.css";

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
        <div className="header-top">
            <TopHeader />
        </div>
    );
};

export default Header;
