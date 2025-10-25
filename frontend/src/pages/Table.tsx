import Header from "../components/Header";
import NavBar from "../components/NavBar";
import Footer from "../components/Footer";
import StandingTable from "../components/StandingTable";

const Table = () => {
    return (
        <div className="min-h-screen flex flex-col">
            <header className="bg-gradient-to-br from-primary to-primary-light shadow-card sticky top-0 z-50">
                <Header />
                <NavBar />
            </header>
            <main className="flex-1">
                <StandingTable />
            </main>
            <footer>
                <Footer />
            </footer>
        </div>
    );
};

export default Table;
