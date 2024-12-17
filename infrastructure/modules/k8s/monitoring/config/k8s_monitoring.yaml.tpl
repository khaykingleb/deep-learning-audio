# Cluster settings
cluster:
  # -- The name of this cluster, which will be set in all labels. Required.
  name: ${cluster_name}

externalServices:
# Connection information for Prometheus
  prometheus:
    # -- Prometheus host where metrics will be sent
    host: "${grafana_prometheus_host}"

    # Authenticate to Prometheus using basic authentication
    basicAuth:
      # -- Prometheus basic auth username
      username: "${grafana_prometheus_username}"
      # -- Prometheus basic auth password
      password: "${grafana_access_policy_token}"

  # Connection information for Grafana Loki
  loki:
    # -- Loki host where logs and events will be sent
    host: "${grafana_loki_host}"

    # Authenticate to Loki using basic authentication
    basicAuth:
      # -- Loki basic auth username
      username: "${grafana_loki_username}"
      # -- Loki basic auth password
      password: "${grafana_access_policy_token}"

# Settings related to capturing and forwarding metrics
metrics:
  # -- Capture and forward metrics
  enabled: true

  # -- How frequently to scrape metrics
  scrapeInterval: 60s

  # -- Rule blocks to be added to the discovery.relabel component for all metric sources.
  # See https://grafana.com/docs/agent/latest/flow/reference/components/discovery.relabel/#rule-block
  extraRelabelingRules: |-
    rule {
      action = "replace"
      source_labels = ["__meta_kubernetes_pod_node_name"]
      target_label = "node"
    }

  # Annotation-based autodiscovery allows for discovering metric sources solely on their annotations and does
  # not require adding any extra configuration.
  autoDiscover:
    # Enable annotation-based autodiscovery
    enabled: true

    # -- Annotations that are used to discover and configure metric scraping targets. Add these annotations
    # to your services or pods to control how autodiscovery will find and scrape metrics from your service or pod.
    annotations:
      # -- Annotation for enabling scraping for this service or pod. Value should be either "true" or "false"
      scrape: "k8s.grafana.com/scrape"
      # -- Annotation for setting or overriding the metrics path. If not set, it defaults to /metrics
      metricsPath: "k8s.grafana.com/metrics.path"
      # -- Annotation for setting the metrics port by number.
      metricsPortNumber: "k8s.grafana.com/metrics.portNumber"

  # Metrics from Grafana Alloy
  alloy:
    # -- Scrape metrics from Grafana Alloy
    enabled: false

    # -- How frequently to scrape metrics from Grafana Alloy
    # Overrides metrics.scrapeInterval
    # @default -- 60s
    scrapeInterval: ""

  # Cluster object metrics from Kube State Metrics
  kube-state-metrics:
    # -- Scrape cluster object metrics from Kube State Metrics
    enabled: true

    # -- How frequently to scrape metrics from Kube State Metrics.
    # Overrides metrics.scrapeInterval
    # @default -- 60s
    scrapeInterval: ""

    # Adjustments to the scraped metrics to filter the amount of data sent to storage.
    metricsTuning:
      # -- Filter the list of metrics from Kube State Metrics to a useful, minimal set. See https://github.com/grafana/k8s-monitoring-helm/blob/85d679e23af4e79eeaae5f2207237e30fef06ff8/charts/k8s-monitoring/README.md#allow-list-for-kube-state-metrics
      useDefaultAllowList: true
      # -- Metrics to keep. Can use regex.
      includeMetrics:
        - kube_pod_status_qos_class
        - kube_namespace_created
        - kube_deployment_status_replicas_unavailable
        - kube_pod_container_status_restarts_total
        - kube_node_labels
      # -- Metrics to drop. Can use regex.
      excludeMetrics:
        - kube_lease_owner
        - kube_lease_renew_time
        - kube_pod_tolerations
        - kube_pod_status_ready
        - kube_pod_status_scheduled
        - kube_pod_owner
        - kube_pod_start_time
        - kube_pod_container_state_started
        - kube_node_status_allocatable
        - kube_node_spec_unschedulable
        - kube_pod_created
        - kube_pod_ips
        - kube_pod_restart_policy
        - kube_pod_service_account
        - kube_pod_status_initialized_time
        - kube_pod_status_scheduled_time
        - kube_pod_status_container_ready_time
        - kube_pod_status_ready_time
        - kube_horizontalpodautoscaler_status_condition
        - kube_replicaset_created
        - kube_replicaset_metadata_generation
        - kube_replicaset_spec_replicas
        - kube_replicaset_status_fully_labeled_replicas
        - kube_replicaset_status_observed_generation
        - kube_replicaset_status_ready_replicas
        - kube_replicaset_status_replicas
        - kube_daemonset_created
        - kube_daemonset_metadata_generation
        - kube_deployment_status_condition
        - kube_namespace_status_phase
        - kube_endpoint_ports
        - kube_endpoint_address
        - kube_secret_created
        - kube_secret_metadata_resource_version

  # Node metrics from Node Exporter
  node-exporter:
    # -- Scrape node metrics
    enabled: true

    # -- How frequently to scrape metrics from Node Exporter.
    # Overrides metrics.scrapeInterval
    # @default -- 60s
    scrapeInterval: ""

    # Adjustments to the scraped metrics to filter the amount of data sent to storage.
    metricsTuning:
      # -- Filter the list of metrics from Node Exporter to the minimal set required for Kubernetes Monitoring. See https://github.com/grafana/k8s-monitoring-helm/blob/85d679e23af4e79eeaae5f2207237e30fef06ff8/charts/k8s-monitoring/README.md#allow-list-for-node-exporter
      useDefaultAllowList: true
      # -- Filter the list of metrics from Node Exporter to the minimal set required for Kubernetes Monitoring as well as the Node Exporter integration.
      useIntegrationAllowList: false
      # -- Metrics to keep. Can use regex.
      includeMetrics:
        - node_uname_info
        - node_time_seconds
        - node_boot_time_seconds
        - node_cpu_core_throttles_total
        - node_load1
        - node_context_switches_total
        - node_filefd_maximum
        - node_timex_estimated_error_seconds
        - node_network_receive_bytes_total
        - node_network_receive_errs_total
        - node_network_receive_packets_total
        - node_network_receive_drop_total
        - node_netstat_Tcp_CurrEstab
        - node_nf_conntrack_entries
        - node_disk_read_bytes_total
        - node_disk_written_bytes_total
        - node_disk_reads_completed_total
        - node_disk_writes_completed_total
        - node_disk_io_now
      # -- Metrics to drop. Can use regex.
      excludeMetrics:
        - node_filesystem_readonly
        - node_filesystem_free_bytes
        - node_scrape_collector_duration_seconds
        - node_scrape_collector_success
        - node_cpu_guest_seconds_total

  # Cluster metrics from the Kubelet
  kubelet:
    # -- Scrape cluster metrics from the Kubelet
    enabled: true

    # -- How frequently to scrape metrics from the Kubelet.
    # Overrides metrics.scrapeInterval
    # @default -- 60s
    scrapeInterval: ""

    # Adjustments to the scraped metrics to filter the amount of data sent to storage.
    metricsTuning:
      # -- Filter the list of metrics from the Kubelet to the minimal set required for Kubernetes Monitoring. See https://github.com/grafana/k8s-monitoring-helm/blob/85d679e23af4e79eeaae5f2207237e30fef06ff8/charts/k8s-monitoring/README.md#allow-list-for-kubelet
      useDefaultAllowList: true
      # -- Metrics to keep. Can use regex.
      includeMetrics: []
      # -- Metrics to drop. Can use regex.
      includeMetrics:
        - kubelet_volume_stats_used_bytes
        - kubelet_volume_stats_capacity_bytes
        - kubelet_volume_stats_inodes_used
        - kubelet_volume_stats_inodes
      excludeMetrics:
        - kubelet_pod_worker_duration_seconds_bucket
        - kubelet_cgroup_manager_duration_seconds_bucket
        - kubelet_runtime_operations_total
        - kubelet_pleg_relist_duration_seconds_bucket
        - kubelet_pleg_relist_interval_seconds_bucket
        - kubelet_pod_start_duration_seconds_bucket
        - rest_client_requests_total
        - storage_operation_duration_seconds_count
        - volume_manager_total_volumes

  # Container metrics from cAdvisor
  cadvisor:
    # -- Scrape container metrics from cAdvisor
    enabled: true

    # -- How frequently to scrape metrics from cAdvisor.
    # Overrides metrics.scrapeInterval
    # @default -- 60s
    scrapeInterval: ""

    # Adjustments to the scraped metrics to filter the amount of data sent to storage.
    metricsTuning:
      # -- Filter the list of metrics from cAdvisor to the minimal set required for Kubernetes Monitoring. See https://github.com/grafana/k8s-monitoring-helm/blob/85d679e23af4e79eeaae5f2207237e30fef06ff8/charts/k8s-monitoring/README.md#allow-list-for-cadvisor
      useDefaultAllowList: true
      # -- Metrics to keep. Can use regex.
      includeMetrics:
        - machine_cpu_cores
        - container_oom_events_total
        - container_network_receive_errors_total
        - container_cpu_cfs_throttled_seconds_total
      # -- Metrics to drop. Can use regex.
      excludeMetrics:
        - container_memory_cache
        - container_memory_swap
        - container_fs_reads_total
        - container_fs_writes_total
        - container_fs_reads_bytes_total
        - container_fs_writes_bytes_total

  # Metrics from the API Server
  apiserver:
    # -- Scrape metrics from the API Server
    enabled: false

    # -- How frequently to scrape metrics from the API Server
    # Overrides metrics.scrapeInterval
    # @default -- 60s
    scrapeInterval: ""

  # Metrics from the Kube Controller Manager
  kubeControllerManager:
    # -- Scrape metrics from the Kube Controller Manager
    enabled: false

    # -- How frequently to scrape metrics from the Kube Controller Manager
    # Overrides metrics.scrapeInterval
    # @default -- 60s
    scrapeInterval: ""

  # Metrics from the Kube Proxy
  kubeProxy:
    # -- Scrape metrics from the Kube Proxy
    enabled: false

    # -- How frequently to scrape metrics from the Kube Proxy
    # Overrides metrics.scrapeInterval
    # @default -- 60s
    scrapeInterval: ""

  # Metrics from the Kube Scheduler
  kubeScheduler:
    # -- Scrape metrics from the Kube Scheduler
    enabled: false

    # -- How frequently to scrape metrics from the Kube Scheduler
    # Overrides metrics.scrapeInterval
    # @default -- 60s
    scrapeInterval: ""

  # Cost related metrics from OpenCost
  cost:
    # -- Scrape cost metrics from OpenCost
    enabled: false

    # -- How frequently to scrape metrics from OpenCost.
    # Overrides metrics.scrapeInterval
    # @default -- 60s
    scrapeInterval: ""

  podMonitors:
    # -- Include service discovery for PodMonitor objects
    enabled: false

    # -- Which namespaces to look for PodMonitor objects.
    namespaces: []

    # -- How frequently to scrape metrics from PodMonitor objects. Only used if the PodMonitor does not specify the scrape interval.
    # Overrides metrics.scrapeInterval
    # @default -- 60s
    scrapeInterval: ""

  probes:
    # -- Include service discovery for Probe objects.
    enabled: false

    # -- Which namespaces to look for Probe objects.
    namespaces: []

    # -- How frequently to scrape metrics from Probe objects. Only used if the Probe does not specify the scrape interval.
    # Overrides metrics.scrapeInterval
    # @default -- 60s
    scrapeInterval: ""

  serviceMonitors:
    # -- Include service discovery for ServiceMonitor objects
    enabled: true

    # -- Which namespaces to look for ServiceMonitor objects.
    namespaces: []

    # -- How frequently to scrape metrics from ServiceMonitor objects. Only used if the ServiceMonitor does not specify the scrape interval.
    # Overrides metrics.scrapeInterval
    # @default -- 60s
    scrapeInterval: ""

  kubernetesMonitoring:
    # -- Report telemetry about this Kubernetes Monitoring chart as a metric.
    enabled: true

# Settings related to capturing and forwarding logs
logs:
  # -- Capture and forward logs
  enabled: true

  # Settings for Kubernetes pod logs
  pod_logs:
    # -- Capture and forward logs from Kubernetes pods
    enabled: true

    # Controls the behavior of discovering pods for logs.
    # When set to "all", every pod (filtered by the namespaces list below) will have their logs gathered, but you can
    # use the annotation to remove a pod from that list.
    # When set to "annotation", only pods with the annotation set to true will be gathered.
    # Possible values: "all" "annotation"
    discovery: "all"

    # The annotation to control the behavior of gathering logs from this pod. If you put this annotation on to your pod,
    # it will either enable or disable auto gathering of logs from this pod.
    annotation: "k8s.grafana.com/logs.autogather"

    # -- Only capture logs from pods in these namespaces (`[]` means all namespaces)
    namespaces: []

  # Settings for scraping Kubernetes cluster events
  cluster_events:
    # -- Scrape Kubernetes cluster events
    enabled: false

    # -- Log format used to forward cluster events. Allowed values: `logfmt` (default), `json`.
    logFormat: "logfmt"

    # -- List of namespaces to watch for events (`[]` means all namespaces)
    namespaces: []

# Settings related to capturing and forwarding traces
traces:
  # -- Receive and forward traces.
  enabled: false

# Settings for the Kube State Metrics deployment
# You can use this sections to make modifications to the Kube State Metrics deployment.
# See https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-state-metrics for available values.
kube-state-metrics:
  # -- Should this helm chart deploy Kube State Metrics to the cluster.
  # Set this to false if your cluster already has Kube State Metrics, or if you
  # do not want to scrape metrics from Kube State Metrics.
  # @section -- Deployment: [Kube State Metrics](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-state-metrics)
  enabled: true


  # NOTE: allow env label to be propagated on kube-state-metrics
  metricLabelsAllowlist:
    - nodes=[env]

# Settings for the Node Exporter deployment
# You can use this sections to make modifications to the Node Exporter deployment.
# See https://github.com/prometheus-community/helm-charts/tree/main/charts/prometheus-node-exporter for available values.
prometheus-node-exporter:
  # -- Should this helm chart deploy Node Exporter to the cluster.
  # Set this to false if your cluster already has Node Exporter, or if you do
  # not want to scrape metrics from Node Exporter.
  enabled: true

  tolerations:
    - effect: NoSchedule
      operator: Exists
    - effect: NoExecute
      operator: Exists

# Settings for the Node Exporter deployment
# You can use this sections to make modifications to the Node Exporter deployment.
# See https://github.com/prometheus-community/helm-charts/tree/main/charts/prometheus-node-exporter for available values.
# @section -- [Prometheus Node Exporter](https://github.com/prometheus-community/helm-charts/tree/main/charts/prometheus-node-exporter) Chart Values
prometheus-operator-crds:
  # -- Should this helm chart deploy the Prometheus Operator CRDs to the cluster.
  # Set this to false if your cluster already has the CRDs, or if you do not
  # to have Grafana Alloy scrape metrics from PodMonitors, Probes, or ServiceMonitors.
  # @section -- Chart
  enabled: true

# Settings for the OpenCost deployment
# You can use this sections to make modifications to the OpenCost deployment.
# See https://github.com/opencost/opencost-helm-chart for available values.
opencost:
  # -- Should this Helm chart deploy OpenCost to the cluster.
  # Set this to false if your cluster already has OpenCost, or if you do
  # not want to scrape metrics from OpenCost.
  enabled: false

# Settings for the Grafana Alloy instance that gathers pod logs.
# See https://github.com/grafana/alloy/tree/main/operations/helm/charts/alloy for available values.
# @ignored -- This skips including these values in README.md
alloy-logs:
  logging:
    # -- Level at which Alloy log lines should be written.
    # @section -- Chart
    level: info
    # -- Format to use for writing Alloy log lines.
    # @section -- Chart
    format: logfmt

  alloy:
    # This chart is creating the configuration, so the grafana-agent chart does
    # not need to.
    configMap: {create: false}

    # Disabling clustering by default, because the default log gathering format does not require clusters.
    # @ignored
    clustering: {enabled: false}

    mounts:
      # Mount /var/log from the host into the container for log collection.
      # @ignored
      varlog: true

      # Mount /var/lib/docker/containers from the host into the container for log
      # collection. Set to true if your cluster puts log files inside this directory.
      # @ignored
      dockercontainers: false

  controller:
    type: daemonset
    nodeSelector:
      kubernetes.io/os: linux

    # Allow this pod to be scheduled on GPU nodes
    tolerations:
      - effect: NoSchedule
        operator: Exists
      - effect: NoExecute
        operator: Exists
