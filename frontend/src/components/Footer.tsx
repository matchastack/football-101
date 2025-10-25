const sections = {
    About: ["Overview", "Team", "Contact"],
    Services: ["Service 1", "Service 2", "Service 3", "Service 4"],
    User: ["Profile", "Settings", "Sign in"],
};

const FooterSection = (section: string) => {
    return (
        <li key={section}>
            <a
                href="/"
                className="text-white/80 no-underline text-[0.9375rem] font-medium transition-all duration-200 py-2 inline-block hover:text-secondary hover:-translate-y-0.5"
            >
                {section}
            </a>
        </li>
    );
};

const Footer = () => {
    return (
        <footer className="bg-gradient-to-br from-primary to-primary-light text-white py-10 md:py-10 mt-16 border-t border-white/10">
            <div className="flex flex-wrap justify-between items-center max-w-[1400px] mx-auto px-8 gap-6">
                <p className="text-white/60 text-sm text-center md:text-left">
                    Copyright © 2023 All Rights Reserved by Football101
                </p>
                <nav>
                    <ul className="list-none m-0 p-0 flex flex-col md:flex-row gap-3 md:gap-6">
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
