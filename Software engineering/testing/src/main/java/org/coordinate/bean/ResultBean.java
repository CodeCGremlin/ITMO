
package org.coordinate.bean;

import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import jakarta.enterprise.context.SessionScoped;
import jakarta.inject.Named;
import jakarta.persistence.EntityManager;
import jakarta.persistence.EntityManagerFactory;
import jakarta.persistence.Persistence;
import jakarta.persistence.TypedQuery;
import java.io.Serializable;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import org.coordinate.entity.Result;

@Named("ResultBean")
@SessionScoped
public class ResultBean implements Serializable {
    private EntityManagerFactory emf;
    private List<ResultDTO> results;
    private int currentPage = 1;
    private static final int RESULTS_PER_PAGE = 10;
    private int totalPages = 0;

    @PostConstruct
    public void init() {
        try {
            this.emf = Persistence.createEntityManagerFactory("CoordinatePU");
            this.loadResults();
        } catch (Exception e) {
            e.printStackTrace();
            this.results = new ArrayList();
        }

    }

    @PreDestroy
    public void destroy() {
        if (this.emf != null && this.emf.isOpen()) {
            this.emf.close();
        }

    }

    public void loadResults() {
        EntityManager em = null;

        try {
            em = this.emf.createEntityManager();
            TypedQuery<Result> query = em.createQuery("SELECT r FROM Result r ORDER BY r.checkTime DESC", Result.class);
            List<Result> entities = query.getResultList();
            this.results = new ArrayList();

            for(Result r : entities) {
                this.results.add(new ResultDTO(r));
            }

            this.totalPages = (int)Math.ceil((double)this.results.size() / (double)10.0F);
            if (this.currentPage > this.totalPages && this.totalPages > 0) {
                this.currentPage = this.totalPages;
            }
        } catch (Exception e) {
            e.printStackTrace();
            this.results = new ArrayList();
            this.totalPages = 0;
        } finally {
            if (em != null) {
                em.close();
            }

        }

    }

    public void addResult(double x, double y, double r, boolean hit) {
        Result result = new Result(x, y, r, hit, LocalDateTime.now(), 0L);
        ResultDTO dto = new ResultDTO(result);
        this.results.add(0, dto);
        EntityManager em = null;

        try {
            em = this.emf.createEntityManager();
            em.getTransaction().begin();
            em.persist(result);
            em.getTransaction().commit();
        } catch (Exception e) {
            if (em != null && em.getTransaction().isActive()) {
                em.getTransaction().rollback();
            }

            e.printStackTrace();
        } finally {
            if (em != null) {
                em.close();
            }

        }

        this.loadResults();
    }

    public void clearAll() {
        EntityManager em = null;

        try {
            em = this.emf.createEntityManager();
            em.getTransaction().begin();
            em.createQuery("DELETE FROM Result").executeUpdate();
            em.getTransaction().commit();
            this.results.clear();
            this.currentPage = 1;
            this.totalPages = 0;
        } catch (Exception e) {
            if (em != null && em.getTransaction().isActive()) {
                em.getTransaction().rollback();
            }

            e.printStackTrace();
        } finally {
            if (em != null) {
                em.close();
            }

        }

    }

    public List<ResultDTO> getResultsForCurrentPage() {
        if (this.results != null && !this.results.isEmpty()) {
            int fromIndex = (this.currentPage - 1) * 10;
            int toIndex = Math.min(fromIndex + 10, this.results.size());
            return (List<ResultDTO>)(fromIndex >= this.results.size() ? new ArrayList() : this.results.subList(fromIndex, toIndex));
        } else {
            return new ArrayList();
        }
    }

    public List<ResultDTO> getAllResults() {
        return (List<ResultDTO>)(this.results == null ? new ArrayList() : this.results);
    }

    public String getAllPointsJson() {
        if (this.results != null && !this.results.isEmpty()) {
            StringBuilder json = new StringBuilder("[");

            for(int i = 0; i < this.results.size(); ++i) {
                ResultDTO dto = (ResultDTO)this.results.get(i);
                json.append("{");
                json.append("\"x\":").append(dto.getX()).append(",");
                json.append("\"y\":").append(dto.getY()).append(",");
                json.append("\"r\":").append(dto.getR()).append(",");
                json.append("\"hit\":").append(dto.getHit() ? "true" : "false");
                json.append("}");
                if (i < this.results.size() - 1) {
                    json.append(",");
                }
            }

            json.append("]");
            return json.toString();
        } else {
            return "[]";
        }
    }

    public List<Integer> getPageNumbersToShow() {
        List<Integer> pages = new ArrayList();
        if (this.totalPages <= 7) {
            for(int i = 1; i <= this.totalPages; ++i) {
                pages.add(i);
            }
        } else if (this.currentPage <= 4) {
            for(int i = 1; i <= 5; ++i) {
                pages.add(i);
            }

            pages.add(-1);
            pages.add(this.totalPages);
        } else if (this.currentPage >= this.totalPages - 3) {
            pages.add(1);
            pages.add(-1);

            for(int i = this.totalPages - 4; i <= this.totalPages; ++i) {
                pages.add(i);
            }
        } else {
            pages.add(1);
            pages.add(-1);

            for(int i = this.currentPage - 1; i <= this.currentPage + 1; ++i) {
                pages.add(i);
            }

            pages.add(-1);
            pages.add(this.totalPages);
        }

        return pages;
    }

    public void firstPage() {
        this.currentPage = 1;
    }

    public void previousPage() {
        if (this.currentPage > 1) {
            --this.currentPage;
        }

    }

    public void nextPage() {
        if (this.currentPage < this.totalPages) {
            ++this.currentPage;
        }

    }

    public void lastPage() {
        this.currentPage = this.totalPages;
    }

    public void goToPage(int page) {
        if (page >= 1 && page <= this.totalPages) {
            this.currentPage = page;
        }

    }

    public int getCurrentPage() {
        return this.currentPage;
    }

    public int getTotalPages() {
        return this.totalPages;
    }

    public int getTotalResults() {
        return this.results != null ? this.results.size() : 0;
    }

    public boolean isFirstPage() {
        return this.currentPage == 1;
    }

    public boolean isLastPage() {
        return this.currentPage == this.totalPages || this.totalPages == 0;
    }

    public List<ResultDTO> getResults() {
        return this.results;
    }

    public void setResults(List<ResultDTO> results) {
        this.results = results;
    }

    public static class ResultDTO implements Serializable {
        private static final DateTimeFormatter FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
        private Double x;
        private Double y;
        private Double r;
        private Boolean hit;
        private String timestamp;

        public ResultDTO(Result result) {
            this.x = result.getX();
            this.y = result.getY();
            this.r = result.getR();
            this.hit = result.getHit();
            this.timestamp = result.getCheckTime().format(FORMATTER);
        }

        public Double getX() {
            return this.x;
        }

        public Double getY() {
            return this.y;
        }

        public Double getR() {
            return this.r;
        }

        public Boolean getHit() {
            return this.hit;
        }

        public String getTimestamp() {
            return this.timestamp;
        }

        public void setX(Double x) {
            this.x = x;
        }

        public void setY(Double y) {
            this.y = y;
        }

        public void setR(Double r) {
            this.r = r;
        }

        public void setHit(Boolean hit) {
            this.hit = hit;
        }

        public void setTimestamp(String timestamp) {
            this.timestamp = timestamp;
        }
    }
}
