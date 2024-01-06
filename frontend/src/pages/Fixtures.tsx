import Header from "../components/Header";
import NavBar from "../components/NavBar";
import Footer from "../components/Footer";
import FixtureList from "../components/FixtureList";

const Table = () => {
    return (
        <>
            <header className="header-top">
                <Header />
                <NavBar />
            </header>
            <body>
                <FixtureList />
            </body>
            <footer>
                <Footer />
            </footer>
        </>
    );
};

export default Table;
