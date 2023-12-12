import "./Header.css";

const Header = () => {
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

export default Header;
