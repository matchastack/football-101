import "./Footer.css";

const sections = {
    About: ["Overview", "Team", "Contact"],
    Services: ["Service 1", "Service 2", "Service 3", "Service 4"],
    User: ["Profile", "Settings", "Sign in"],
};

const FooterSection = (section: string) => {
    return (
        <li>
            <a href="/">{section}</a>
        </li>
    );
};

const Footer = () => {
    return (
        <footer className="footer">
            <div className="footer-content">
                <p>Copyright © 2023 All Rights Reserved by Football101</p>
                <nav>
                    <ul>
                        {Object.keys(sections).map((section) =>
                            FooterSection(section)
                        )}
                    </ul>
                </nav>
            </div>
        </footer>
    );
};

export default Footer;
