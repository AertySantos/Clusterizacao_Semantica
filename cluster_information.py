import sys
import os
import warnings
import collections
import scipy as sp
import numpy as np
from scipy import io
from scipy.optimize import minimize_scalar
from sklearn.cluster import SpectralClustering, AgglomerativeClustering, MiniBatchKMeans, AffinityPropagation, Birch, DBSCAN,KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score, pairwise_distances, normalized_mutual_info_score, adjusted_rand_score
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

class Clustering:

    def __init__(self, data_, matrixpath_, outputpath_=None, distance_=None, metric_="cosine", n_clusters_=0, optimization_="silhouette", algorithm_="spectral", labels_=[], idxfocus_=None, grafico_= False):
        self.data = data_
        self.grafico = grafico_

        if distance_ == [] or distance_ == None:
            warnings.filterwarnings('ignore', message='Metric applies a coversion.')
            self.distance_mtx = pairwise_distances(data_, metric=metric_, n_jobs=None)
        else:
            self.distance_mtx = distance_
        self.idxfocus = idxfocus_
        self.metric = metric_
        self.matrixpath = matrixpath_
        if outputpath_ == None or outputpath_ == "":
            self.outputpath = matrixpath_
        else:
            self.outputpath = outputpath_
        self.optimization = optimization_
        self.labels = labels_
        self.algorithm = algorithm_
        self.cluster_min = 2
        self.cluster_max = self._choose_max_k(np.shape(data_)[0])
        if n_clusters_ < self.cluster_min:
            self.n_clusters = self.cluster_min
        elif n_clusters_ > self.cluster_max:
            self.n_clusters = self.cluster_max
        else:
            self.n_clusters = n_clusters_


    def _choose_max_k(self, dataset_size):
        '''
        [ Jiawei Han et.al. 2011 - Data Mining Concepts and Techniques]
        simple k_cluster guess method is [sqrt(dataset size/2)]
        'elbow method', metric evaluation to define better results achieved for each k value.
        '''
        k = int(round((dataset_size / 2) ** 0.5))
        if dataset_size < 5000:
            k = k * 2
        return k

    def plot_clusters(self, cluster_labels):
        """
        Gera um gráfico de dispersão verificando se os dados estão em 2D. 
        Se não estiverem, reduz para 2D usando PCA.
        
        Args:
            cluster_labels (array): Rótulos dos clusters gerados.
        """
        # Verifica a dimensionalidade dos dados
        if self.data.shape[1] != 2:
            #print("[Info] Dados não estão em 2D. Aplicando PCA para redução de dimensionalidade.")
            pca = PCA(n_components=2)
            data_2d = pca.fit_transform(self.data)
        else:
            #print("[Info] Dados já estão em 2D. Nenhuma transformação será aplicada.")
            data_2d = self.data
        
        # Cria o gráfico de dispersão
        plt.figure(figsize=(10, 8))
        # Armazena os centroides
        centroids = []

        num_centroids = len(np.unique(cluster_labels))

        for cluster in np.unique(cluster_labels):
            # Obtém os pontos do cluster
            cluster_points = data_2d[np.where(cluster_labels == cluster)]
            
            # Plota os pontos do cluster
            plt.scatter(cluster_points[:, 0], cluster_points[:, 1], label=f'Cluster {cluster}', alpha=0.6)
            
            # Calcula o centroide e armazena
            centroid = np.mean(cluster_points, axis=0)
            centroids.append(centroid)
         # Calcula os centroides
        centroids = np.array([data_2d[np.where(cluster_labels == cluster)].mean(axis=0) for cluster in np.unique(cluster_labels)])
        
        # Plota os centroides com um rótulo comum
        plt.scatter(centroids[:, 0], centroids[:, 1], color='black', marker='x', s=100, label='Centroide')

        # Configurações do gráfico
        plt.title(f"Visualização de Clusters com K = {num_centroids}", fontsize=14)
        plt.xlabel("Dimensão 1", fontsize=12)
        plt.ylabel("Dimensão 2", fontsize=12)
        plt.legend()
        plt.grid(True)
        plt.savefig("data/output/graficos/kmeans.png")
    """
    Evaluation
    """
    def _sse(self, cluster_labels):
        # Initialise Sum of Squared Errors
        # add self.idxfocus method
        sse = 0
        if self.idxfocus != None:
            clusters = [cluster_labels[i] for i in self.idxfocus]
            for c in np.unique(clusters):
                cluster = np.where(clusters == c)[0]
                centroid = np.mean(self.data[cluster, :], axis=0).reshape(1, -1)
                sim = 0
                for c in cluster:
                    sim += pairwise_distances(self.data[c].reshape(1, -1), centroid, metric="l2", n_jobs=None)[0, 0] # l2 - squared euclidean
                sse = sse + (sim/len(cluster))
        else:
            for c in np.unique(cluster_labels):
                cluster = np.where(cluster_labels == c)[0]
                centroid = np.mean(self.data[cluster, :], axis=0).reshape(1, -1)
                sim = 0
                for c in cluster:
                    sim += pairwise_distances(self.data[c].reshape(1, -1), centroid, metric="l2", n_jobs=None)[0, 0] # l2 - squared euclidean
                sse = sse + (sim/len(cluster))
        return sse


    def _silhouette(self, cluster_labels):
        if self.idxfocus != None:
            return silhouette_score(self.distance_mtx[self.idxfocus, :][:, self.idxfocus], cluster_labels[self.idxfocus], metric="precomputed")
        else:
            return silhouette_score(self.distance_mtx, cluster_labels, metric="precomputed")


    def _davies_bouldin(self, cluster_labels):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            if self.idxfocus != None:
                return davies_bouldin_score(self.data[self.idxfocus, :], cluster_labels[self.idxfocus])
            else:
                return davies_bouldin_score(self.data, cluster_labels)


    def _calinski_harabasz(self, cluster_labels):
        if self.idxfocus != None:
            return calinski_harabasz_score(self.data[self.idxfocus, :], cluster_labels[self.idxfocus])
        else:
            return calinski_harabasz_score(self.data, cluster_labels)

    
    def _cv_distance(self, cluster_labels):
        cluster_dist = []
        if self.idxfocus != None:
            clusters = [cluster_labels[i] for i in self.idxfocus]
            for c in np.unique(clusters):
                cluster = np.where(clusters == c)[0]
                sim = []
                for id1, c1 in enumerate(cluster):
                    for id2, c2 in enumerate(cluster):
                        if id2 > id1: # usar precomputed
                            sim.append(self.distance_mtx[self.idxfocus[c1], self.idxfocus[c2]])
                if sim != []:
                    cluster_dist.append(np.mean(sim))
                else:
                    cluster_dist.append(0.0)
        else:
            for c in np.unique(cluster_labels):
                cluster = np.where(cluster_labels == c)[0]
                sim = []
                for id1, c1 in enumerate(cluster):
                    for id2, c2 in enumerate(cluster):
                        if id2 > id1: # usar precomputed
                            sim.append(self.distance_mtx[c1, c2])
                if sim != []:
                    cluster_dist.append(np.mean(sim))
                else:
                    cluster_dist.append(0.0)
        if np.mean(cluster_dist) == 0:
            return 0
        return np.std(cluster_dist)/np.mean(cluster_dist)


    def _cv_size(self, cluster_labels):
        cluster_size = []
        if self.idxfocus != None:
            clusters = [cluster_labels[i] for i in self.idxfocus]
            for c in np.unique(clusters):
                cltr = np.where(clusters == c)[0]
                cluster_size.append(len(cltr))
        else:
            for c in np.unique(cluster_labels):
                cltr = np.where(cluster_labels == c)[0]
                cluster_size.append(len(cltr))
        if np.mean(cluster_size) == 0:
            return 0
        return ((np.max(cluster_size) - np.min(cluster_size)) / len(cluster_size)) / sum(cluster_size)


    """
    Algorithms
    """
    ## algorithms:  'cluto', 'libDocumento', 'agglomerative', 'spectral', 'kmeans', 'minibatch', 'birch', 'affinity', 'dbscan'



    def _run_agglomerative(self):
        # Aplica o AgglomerativeClustering
        clustering_agglomerative = AgglomerativeClustering(
            n_clusters=self.n_clusters, linkage="complete", metric="precomputed"
        ).fit_predict(self.distance_mtx)

        if self.grafico:
            # Verifica a dimensionalidade dos dados e aplica PCA, se necessário
            if self.data.shape[1] != 2:
                pca = PCA(n_components=2)
                data_2d = pca.fit_transform(self.data)
            else:
                data_2d = self.data

            # Calcula os centróides dos clusters
            centroids = np.array([
                data_2d[np.where(clustering_agglomerative == cluster)].mean(axis=0)
                for cluster in np.unique(clustering_agglomerative)
            ])

            # Plota os clusters
            plt.figure(figsize=(10, 8))
            scatter = plt.scatter(
                data_2d[:, 0], data_2d[:, 1], c=clustering_agglomerative, cmap="tab10",
                marker="o", edgecolors="k", alpha=0.7, s=80, label="Pontos"
            )

            # Plota os centroides
            plt.scatter(
                centroids[:, 0], centroids[:, 1], color='black', marker='X',
                s=200, label='Centroide', edgecolors='white', linewidth=1.5
            )

            # Adiciona a barra de cores para indicar os clusters
            plt.colorbar(scatter, label="Cluster")

            # Configurações do gráfico
            plt.xlabel("Dimensão 1", fontsize=14)
            plt.ylabel("Dimensão 2", fontsize=14)
            plt.title(f"Agglomerative Clustering (n_clusters={self.n_clusters})", fontsize=16)
            plt.legend(loc="best", fontsize=12)
            plt.grid(True, linestyle='--', alpha=0.5)

            # Salva o gráfico com melhor qualidade
            plt.savefig("data/output/graficos/agglomerative_clustering.png", dpi=300, bbox_inches="tight")
            plt.show()

        return clustering_agglomerative


    def _run_spectral(self):
        cluster_labels = SpectralClustering(
            n_clusters=self.n_clusters, eigen_solver=None, affinity="precomputed"
        ).fit_predict(self.distance_mtx)

        if self.grafico:
            # Redução de dimensionalidade para visualização
            if self.data.shape[1] != 2:
                #print("[Info] Dados não estão em 2D. Aplicando PCA para redução de dimensionalidade.")
                pca = PCA(n_components=2)
                data_2d = pca.fit_transform(self.data)
            else:
            # print("[Info] Dados já estão em 2D. Nenhuma transformação será aplicada.")
                data_2d = self.data

            # Calcula os centróides estimados dos clusters
            centroids = np.array([
                data_2d[np.where(cluster_labels == cluster)].mean(axis=0)
                for cluster in np.unique(cluster_labels)
            ])

            # Plotando os pontos dos clusters
            plt.figure(figsize=(8, 6))
            plt.scatter(
                data_2d[:, 0], data_2d[:, 1], c=cluster_labels, cmap="viridis",
                marker="o", edgecolors="k", alpha=0.7, label="Pontos"
            )

            # Plotando os centróides estimados
            plt.scatter(
                centroids[:, 0], centroids[:, 1], color='black', marker='x',
                s=100, label='Centroide'
            )

            # Configurações do gráfico
            plt.xlabel("Dimensão 1", fontsize=12)
            plt.ylabel("Dimensão 2", fontsize=12)
            plt.title(f"Spectral Clustering (n_clusters={self.n_clusters})", fontsize=14)
            plt.legend()
            plt.grid(True)

            # Salvar o gráfico
            plt.savefig("data/output/graficos/spectral_clustering.png", dpi=300, bbox_inches="tight")
            plt.show()

        return cluster_labels

    def _run_dbscan(self):
        """
        DBSCAN cannot integrate the module to solve all problems using its default configuration.
        The proximity distance method sometimes return as result all negative (outliers) or single cluster values.
        That is not expected on optimization module and number of clusters selection method.
        Is highly recommended to use DBSCAN just as baseline model while not supported.
        
        DBSCAN issues example:
        >>> [-1, -1, -1, ..., -1, -1, -1]
        >>> [0, 0, 0, ..., 0, 0, 0]
        In both cases we solve throwing a null vector as result [], this approach needs to be solved in an upper level (caller).
        """
        # float(1/self.n_clusters) may be evaluated by some tests to prove efficiency
        
        # Aplica DBSCAN com matriz de distância pré-computada
        labels = DBSCAN(eps=float(1/self.n_clusters), metric="precomputed").fit_predict(self.distance_mtx)
        if self.grafico:
            # Redução de dimensionalidade para visualização
            if self.data.shape[1] != 2:
                #print("[Info] Dados não estão em 2D. Aplicando PCA para redução de dimensionalidade.")
                pca = PCA(n_components=2)
                data_2d = pca.fit_transform(self.data)
            else:
                #print("[Info] Dados já estão em 2D. Nenhuma transformação será aplicada.")
                data_2d = self.data

            # Identifica os clusters e os outliers
            unique_labels = np.unique(labels)
            colors = plt.cm.viridis(np.linspace(0, 1, len(unique_labels)))
            
            plt.figure(figsize=(8, 6))

            # Plota cada cluster com uma cor diferente
            for cluster, color in zip(unique_labels, colors):
                if cluster == -1:
                    # Outliers são plotados em vermelho
                    color = "red"
                    label = "Outlier"
                else:
                    label = f"Cluster {cluster}"
                
                plt.scatter(
                    data_2d[labels == cluster, 0], data_2d[labels == cluster, 1],
                    c=[color], marker="o", edgecolors="k", alpha=0.7, label=label
                )

            # Configurações do gráfico
            plt.xlabel("Dimensão 1", fontsize=12)
            plt.ylabel("Dimensão 2", fontsize=12)
            plt.title(f"DBSCAN Clustering (eps={1/self.n_clusters})", fontsize=14)
            plt.legend()
            plt.grid(True)

            # Salvar o gráfico
            plt.savefig("data/output/graficos/dbscan_clustering.png", dpi=300, bbox_inches="tight")
            plt.show()

        return labels
    

    def _run_kmeans(self):
        """
        Executa o algoritmo K-Means para clusterização.
        """
        
        # Configuração básica para o algoritmo K-Means
        kmeans = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
        
        # Ajusta o modelo com os dados
        kmeans.fit(self.data)

        if self.grafico:
            self.plot_clusters(kmeans.labels_)
       
        # Retorna os rótulos dos clusters
        return kmeans.labels_




    """
    Optimizer
    """
    
    
    def cluster_analysis(self):
        
        # Otimiza número de clusters
        try:
            score, self.n_clusters = self._optimize_n_clusters()
            if self.n_clusters < 2 or self.n_clusters >= len(self.data):
                raise ValueError(f"Número de clusters inválido: {self.n_clusters}")
            print(f"[Debug] Otimização completa: Score = {score}, n_clusters = {self.n_clusters}")
            
            # Executa clustering
            if self.algorithm == "agglomerative":
                cluster_labels = self._run_agglomerative()
            elif self.algorithm == "spectral":
                cluster_labels = self._run_spectral()
            elif self.algorithm == "kmeans":
                cluster_labels = self._run_kmeans()
            elif self.algorithm == "dbscan":
                cluster_labels = self._run_dbscan()
            else:
                return None, -1
            
            return cluster_labels
        except Exception as e:
            print(f"[Error] Falha no processo de clusterização: {e}")
            return None, -1


    def _optimize_n_clusters(self):
        max_iter = self.cluster_max - self.cluster_min
        ntests = int(0.5 * (self.cluster_max - self.cluster_min))
        res = minimize_scalar(self._cluster_metric, bounds=(self.cluster_min, self.cluster_max), options = {"maxiter": ntests})
        
        return res.fun, int(res.x)


    def _cluster_metric(self, k_value):
        
        # Collect the return from skopt
        if type(k_value) == list:
            self.n_clusters = int(k_value[0])
        else:
            self.n_clusters = int(k_value)
        warnings.filterwarnings('ignore', message='The objective has been evaluated at this point before.')
        if self.algorithm == "agglomerative":
            cluster_labels = self._run_agglomerative()
        elif self.algorithm == "spectral":
            cluster_labels = self._run_spectral()
        elif self.algorithm == "dbscan":
            cluster_labels = self._run_dbscan()
        elif self.algorithm == "kmeans":
            cluster_labels = self._run_kmeans()
            
        # Use one of the following methods to optimize clustering parameters
        if self.optimization == "nmi":
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                return -1 * normalized_mutual_info_score(self.labels, cluster_labels)
        elif self.optimization == "ari":
            return -1 * adjusted_rand_score(self.labels, cluster_labels)
        elif self.optimization == "sse":
            return self._sse(cluster_labels)
        elif self.optimization == "cv_size":
            return self._cv_size(cluster_labels)
        elif self.optimization == "cv_distance":
            return self._cv_distance(cluster_labels)
        elif self.optimization == "ch_score":
            return self._calinski_harabasz(cluster_labels)
        elif self.optimization == "db_score":
            return self._davies_bouldin(cluster_labels)
        elif self.optimization =="silhouette":
            return -1 * self._silhouette(cluster_labels) # silhoutte score
        return None


    """
    IO Utils 
    """
    def read_document(self, filename, pathto):
        with open(pathto+filename,"r") as txt:
            return txt.read()


    def save_document(self, filename, filedata, pathto):
        with open(pathto+filename,"w", encoding=self.encoding) as txt:
            return txt.write("\n".join(filedata))


    def save_mm_matrix(self, filename, pathto):
        mm_values = []
        sum_ = 0
        for docid, line in enumerate(self.data):
            for enum, l in enumerate(line):
                if float(l) != 0.0:
                    mm_values.append(str(docid+1)+" "+str(enum+1)+" "+str(l))
                    sum_ += 1
        with open(pathto+filename, 'w') as arq:
            arq.write("% Matrix Market\n")
            arq.write(str(np.shape(self.data)[0])+" "+str(np.shape(self.data)[1])+" "+str(sum_)+"\n")
            for m in mm_values:
                arq.write(str(m)+"\n")


    def load_mm_matrix(self, filename, pathto):
        return io.mmread(pathto+filename)


    def output_check(self, folder):
        try:
            os.stat(folder)
        except:
            os.makedirs(folder)


    def save_csv_document(self, filename, pathto, delimiter_=';'):
        with open(pathto+filename, 'w', newline='\n') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=delimiter_, quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for r in self.data:
                csvwriter.writerow(r)


    def read_matrix(self, filename, pathto, header=True):
        with open(pathto+filename, 'r', encoding=self.encoding) as fh:
            if header:
                var = fh.readline()
                docids, nfeatures = var.replace("\n","").split()
            doclist = []
            docs = fh.read()
            for did in range(int(docids)):
                doclist.append(np.array([float(n) for n in docs.split("\n")[did].split()]))
        return docids, nfeatures, doclist


    def save_matrix(self, filename, pathto, fmt="%.4g", delimiter=' '):
        with open(pathto+filename, 'w') as fh:
            fh.write(str(np.shape(self.data)[0])+" "+str(np.shape(self.data)[1])+"\n")
            for rid in range(np.shape(self.data)[0]):
                #lista = delimiter.join("0" if data[rid,idx] == 0 else fmt % data[rid,idx] for idx in  range(np.shape(data[rid])[1]))
                lista = delimiter.join("0" if self.data[rid, idx] == 0 else fmt % self.data[rid,idx] for idx in  range(np.shape(self.data[rid])[0]))
                fh.write(lista + '\n')

    
    

