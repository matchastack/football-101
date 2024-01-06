import Header from "../components/Header";
import NavBar from "../components/NavBar";
import Footer from "../components/Footer";
import StandingTable from "../components/StandingTable";

const Table = () => {
    return (
        <>
            <header className="header-top">
                <Header />
                <NavBar />
            </header>
            <body>
                <StandingTable />
            </body>
            <footer>
                <Footer />
            </footer>
        </>
    );
};

export default Table;
