package server.manager;



public class AuthManager {
    private final DatabaseManager dbManager;

    public AuthManager(DatabaseManager dbManager) {
        this.dbManager = dbManager;
    }

    public boolean authenticate(String login, String password) {
        return dbManager.authenticate(login, password);
    }

}